# import packages 
import re
from kivy.resources import resource_add_path
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
import auto_size
import interface_stats as inf_stat
from kivy.clock import Clock
from threading import Thread
import interface_info
import port_scanner
from kivy.metrics import dp
import misc
import domain_lookup
import NetworkDiscover
import os,sys
import adress_ping as ap
class Test(MDApp):
    selected_IF = ""
    auto_refresh_interval = 0 # Co ile sekund ma odświeżać dane
    selected_port_filter = "Show open ports"
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path,relative_path)
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self.screen = Builder.load_file("./Layouts/layout.kv") #załadowanie interfejsu z pliku
        #self.screen = Builder.load_file(self.resource_path('Layouts/layout.kv'))
        int_names=inf_stat.interface_data.get_if_names()
        choose = ["Show open ports","Show all"]
        interfaces_menu_items = [
            {
                "text": f"{i}",
                "viewclass": "AutoSizingOneLineListItem",
                "on_release": lambda x=f"{i}": self.interfaces_menu_callback(x),
            } for i in int_names
        ] #pobieranie nazw dostępnych interfejsów do listy rozwijanej
        
        interval_menu_items = [
            {
                "text": f"{i}",
                "viewclass": "AutoSizingOneLineListItem",
                "on_release": lambda x=f"{i}": self.interval_menu_callback(x),
            } for i in range(10+1)
        ]
        
        filter_menu_items = [
            {
                "text": f"{i}",
                "viewclass":"AutoSizingOneLineListItem",
                "on_release": lambda x=f"{i}": self.port_menu_callback(x),
            } for i in choose
        ]
        
        self.menu_if_names = MDDropdownMenu(
            caller=self.screen.ids.select_if_button,
            items=interfaces_menu_items,
            width_mult=auto_size.AutoSizingOneLineListItem.get_max_name_len(int_names)/3,  # Ustawianie szerokości wiersza
        )
        
        self.menu_interval = MDDropdownMenu(
            caller=self.screen.ids.refresh_interval_button,
            items=interval_menu_items,
            width_mult=2,  # Ustawianie szerokości wiersza
        )
        
        self.port_view_menu = MDDropdownMenu(
            caller = self.screen.ids.select_port_filter_button,
            items = filter_menu_items,
            width_mult=4
        )
        self.port_view_menu.text = "Show open ports"
        self.auto_refresh_event = None  # Zmienna przechowująca zdarzenie zegara
        self.auto_refresh_interval = 1
    
    
    def start_auto_refresh(self): #włączanie automatycznego odświeżania danych
        if not self.auto_refresh_event:
            self.auto_refresh_event = Clock.schedule_interval(self.auto_refresh, self.auto_refresh_interval)


    def auto_refresh(self, dt):
        # Utwórz nowy wątek, aby uniknąć blokowania GUI
        t = Thread(target=self.update_interface_data)
        t.start()
        
        
    def update_interface_data(self):
        # Aktualizuj dane interfejsu w nowym wątku
        current_interface = self.selected_IF
        self.packet_data_get_info(current_interface)
        self.get_net_usage_info(current_interface)
        
        
    def stop_auto_refresh(self):
        if self.auto_refresh_event:
            self.auto_refresh_event.cancel()
            self.auto_refresh_event = None


    def interfaces_menu_callback(self, text_item): #menu wyboru dostępnych interfejsów
        self.screen.ids.selected_if_label.text ="Aktualnie wybrany:" + text_item
        current_interface=text_item
        self.selected_IF = current_interface
        self.packet_data_get_info(current_interface)
        self.get_net_usage_info(current_interface)
        self.get_if_info(current_interface)
        self.menu_if_names.dismiss()
        self.start_auto_refresh()
        
        
    def interval_menu_callback(self, text_item): #menu wyboru interwału
        self.auto_refresh_interval = int(text_item)
        self.stop_auto_refresh()
        self.start_auto_refresh()
        self.menu_interval.dismiss()
        

    def port_menu_callback(self, text_item):
        self.screen.ids.select_port_filter_button.text = text_item
        self.selected_port_filter = text_item
        self.port_view_menu.dismiss()


    def get_if_info(self,inf): #pobieranie danych z wybranego interfejsu
        network_info = interface_info.int_info.get_network_info(inf)
        self.screen.ids.int_IP.text = str(network_info[0])
        self.screen.ids.int_MAC.text = str(network_info[1])
        self.screen.ids.int_DNS.text = str(network_info[2])
        self.screen.ids.int_GW.text = str(network_info[3])
        self.screen.ids.int_DHCP.text = str(network_info[4])
        self.screen.ids.int_sub_mask.text = str(network_info[5])
    

    def packet_data_get_info(self,current_interface): #pobieranie danych o pakietach z wybranego interfejsu
        interface_packets_values=inf_stat.interface_data.get_packet_interface_data(current_interface)
        self.screen.ids.int_SNT.text = str(interface_packets_values[0])
        self.screen.ids.int_RCV.text = str(interface_packets_values[1])
        self.screen.ids.int_LST_out.text = str(interface_packets_values[2])
        self.screen.ids.int_LST_in.text = str(interface_packets_values[3])
    
    
    def get_net_usage_info(self,current_interface): #pobieranie danych o prędkości
        interface_speed_values=inf_stat.interface_data.net_usage(current_interface)
        self.screen.ids.int_speed_out.text = str(interface_speed_values[1])
        self.screen.ids.int_speed_in.text = str(interface_speed_values[0])
    
          
    def port_scan(self, ip_addr, port_start, port_end):  # pobieranie danych o przeskanowanych portach oraz wyświetlanie wyników
        self.root.ids.result_layout.clear_widgets()
        scanning_label = MDLabel(text="Skanowanie w toku...", theme_text_color="Secondary", size_hint_y=None, height=dp(40))
        self.root.ids.result_layout.add_widget(scanning_label)

        def callback(scan_results):
            self.root.ids.result_layout.clear_widgets()
            self.root.ids.result_layout.remove_widget(scanning_label)
            sorted_port_list = sorted(scan_results, key=lambda x: int(x.split(" ")[1].split(":")[0]))  # sortowanie po numerach portu
            self.port_view_filter(sorted_port_list, self.selected_port_filter)
                                
        # Utwórz nowy wątek, aby uniknąć blokowania GUI
        t = Thread(target=lambda: self.port_scan_thread(ip_addr, port_start, port_end, callback))
        t.start()


    def port_scan_thread(self, ip_addr, port_start, port_end, callback):
        scan_results = port_scanner.port_scan.scan_ports(ip_addr, port_start, port_end)
        Clock.schedule_once(lambda dt: callback(scan_results))
    
    
    def port_view_filter(self,port_list,option):
        filtered_port_list = misc.Tools.print_list_items(port_list,option)
        for result in filtered_port_list:  # przedstawianie wyników w aplikacji
                label = MDLabel(text=result, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                self.root.ids.result_layout.add_widget(label)     
    
    
    def is_port_button_disabled(self, ip_address, port_start, port_stop):
    # Sprawdzanie czy pola są puste
        if not ip_address or not port_start or not port_stop:
            return True

        # Sprawdzanie czy adres IP jest poprawny
        if not self.root.ids.port_ip_address_input.error:
            return False

        # Jeśli żaden z powyższych warunków nie jest spełniony, przycisk jest zablokowany
        return True 
    
    
    def is_ping_button_disabled(self, ip_address,count):
        if not ip_address:
            return True

        # Sprawdzanie czy adres IP jest poprawny
        if self.root.ids.ping_ip_address_input.error == False and count and count.isdigit() and int(count)>0:
            return False

        # Jeśli żaden z powyższych warunków nie jest spełniony, przycisk jest zablokowany
        return True    
    
    
    def is_discover_button_disabled(self, ip_address):
    # Sprawdzanie czy pola są puste
        if not ip_address:
            return True

        # Sprawdzanie czy adres IP jest poprawny
        if not self.root.ids.network_address_input.error:
            return False

        # Jeśli żaden z powyższych warunków nie jest spełniony, przycisk jest zablokowany
        return True 
    
    
    def is_lookup_button_disabled(self,domain_address):
    # Sprawdzanie czy pola są puste
        if not domain_address:
            return True

        # Sprawdzanie czy adres domeny jest poprawny
        if not self.root.ids.ip_address_input.error:
            return False

        # Jeśli żaden z powyższych warunków nie jest spełniony, przycisk jest zablokowany
        return True  
    
    
    def domain_info(self, domain):
        self.root.ids.dns_result_layout.clear_widgets()
        domain_info = domain_lookup.domain_info.get_domain_info(domain)
        for key, value in domain_info.items():
            label_text = f"{key}: {value}"
            label = MDLabel(text=label_text, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
            self.root.ids.dns_result_layout.add_widget(label)
   
    
    def is_valid_domain_name(self,text): #sprawdzanie poprawnosci nazwy domeny
        domain_pattern = re.compile(r'^(?!:\/\/)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')
        if domain_pattern.match(text):
            self.root.ids.domain_address_input.error = False
        else:
            self.root.ids.domain_address_input.error = True
            self.root.ids.domain_address_input.helper_text = "Invalid domain Address"
    
           
    def check_ip_format(self,text,field_id): #sprawdzanie poprawnosci wpisanego adresu ip
        ip_address_input = self.root.ids[field_id]
        ip_pattern = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'
        )
        if ip_pattern.match(text):
            ip_address_input.error = False
            ip_address_input.helper_text=""
        else:
            ip_address_input.error = True
            ip_address_input.helper_text_mode = "persistent"
            ip_address_input.helper_text = "Invalid IP Address"


    def check_network_format(self, text):
        ip_pattern = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'
            r'/(3[0-2]|[1-2]?[0-9])$'  # Dodatkowo sprawdzany prefix length (0-32)
        )

        network_input = self.root.ids.network_address_input

        if ip_pattern.match(text):
            network_input.error = False
            network_input.helper_text = ""
            
        else:
            network_input.error = True
            network_input.helper_text_mode = "persistent"
            network_input.helper_text = "Invalid network address or mask"
    
      
    def scan_network(self, network):
        device_list = self.root.ids.device_list
        device_list.clear_widgets()
        scanning_label = MDLabel(text="Skanowanie w toku...", theme_text_color="Secondary", size_hint_y=None, height=dp(40))
        self.root.ids.result_layout_scan.add_widget(scanning_label)

        def callback(scan_results):
            self.root.ids.result_layout_scan.remove_widget(scanning_label)
            for device in scan_results:
                label_text = f"IP Address: {device['ip']}, Hostname: {device['hostname']}, MAC Address: {device['mac']}"
                label = MDLabel(text=label_text, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                device_list.add_widget(label)
                                
        t = Thread(target=lambda: self.network_scan_thread(network, callback))
        t.start()

    def network_scan_thread(self, network,callback):
        scan_results = NetworkDiscover.NetworkScanner.scan_network(network)
        Clock.schedule_once(lambda dt: callback(scan_results))
        
    def start_ping_thread(self,ip_addr,num_ping):
        ping_list = self.root.ids.ping_result_layout
        ping_list.clear_widgets()
        # Uruchamiamy wątek do pingowania
        ping_thread = Thread(target=self.ping_thread, args=(ip_addr,num_ping))
        ping_thread.start()

    def ping_thread(self, ip_addr, ping_num):
        # Funkcja zwrotna dla wyników pinga
        def update_callback(result):
            # Aktualizuj wynik w interfejsie użytkownika w głównym wątku
            Clock.schedule_once(lambda dt, r=result: self.update_ping_list(r), 0)

        # Wywołujemy metodę ping_ip z klasy AddressPing
        self.ping_instance.ping_ip(ip_addr, ping_num, update_callback)

    def update_ping_list(self, result):
        # Dodaj wynik pinga do listy w interfejsie użytkownika
        ping_list = self.root.ids.ping_result_layout
        new_label = MDLabel(text=result)
        ping_list.add_widget(new_label)   
        
    def build(self):
        self.ping_instance = ap.adress_ping()
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return self.screen
    
    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Teal" if self.theme_cls.primary_palette == "Red" else "Red"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

if __name__ == '__main__':
    try:
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        Test().run()
    except Exception as e:
        print(e)
        input("Press enter.")

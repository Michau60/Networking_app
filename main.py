# import packages 
import re
import time
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
from kivy.uix.progressbar import ProgressBar

class Test(MDApp):
    selected_IF = ""
    auto_refresh_interval = 0 # Co ile sekund ma odświeżać dane
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self.screen = Builder.load_file("./layouts/general_info.kv") #załadowanie interfejsu z pliku
        int_names=inf_stat.interface_data.get_if_names()
        
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
        
        self.menu_if_names = MDDropdownMenu(
            caller=self.screen.ids.select_if_button,
            items=interfaces_menu_items,
            width_mult=inf_stat.interface_data.get_max_name_len(int_names),  # Ustawianie szerokości wiersza
        )
        
        self.menu_interval = MDDropdownMenu(
            caller=self.screen.ids.refresh_interval_button,
            items=interval_menu_items,
            width_mult=2,  # Ustawianie szerokości wiersza
        )
        
        self.auto_refresh_event = None  # Zmienna przechowująca zdarzenie zegara
        self.auto_refresh_interval = 1
    
    
    def start_auto_refresh(self):
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
        
    
    # def port_scan(self,ip_addr,port_start,port_end): #pobieranie danych o przeskanowanych portach oraz wyświetlanie wyników
    #     self.root.ids.result_layout.clear_widgets()
    #     scan_results=port_scanner.port_scan.scan_ports(ip_addr,port_start,port_end)
    #     sorted_results = sorted(scan_results, key=lambda x: int(x.split(" ")[1].split(":")[0]))#sortowanie po numerach portu
    #     for result in sorted_results: #przedstawianie wyników w aplikacji
    #         label = MDLabel(text=result, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
    #         self.root.ids.result_layout.add_widget(label)
    
    
    def port_scan(self, ip_addr, port_start, port_end):  # pobieranie danych o przeskanowanych portach oraz wyświetlanie wyników
        self.root.ids.result_layout.clear_widgets()
        scanning_label = MDLabel(text="Skanowanie w toku...", theme_text_color="Secondary", size_hint_y=None, height=dp(40))
        self.root.ids.result_layout.add_widget(scanning_label)

        def callback(scan_results):
            self.root.ids.result_layout.clear_widgets()
            self.root.ids.result_layout.remove_widget(scanning_label)
            sorted_results = sorted(scan_results, key=lambda x: int(x.split(" ")[1].split(":")[0]))  # sortowanie po numerach portu
            for result in sorted_results:  # przedstawianie wyników w aplikacji
                label = MDLabel(text=result, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                self.root.ids.result_layout.add_widget(label)

        # Utwórz nowy wątek, aby uniknąć blokowania GUI
        t = Thread(target=lambda: self.port_scan_thread(ip_addr, port_start, port_end, callback))
        t.start()

    def port_scan_thread(self, ip_addr, port_start, port_end, callback):
        scan_results = port_scanner.port_scan.scan_ports(ip_addr, port_start, port_end)
        Clock.schedule_once(lambda dt: callback(scan_results))
    
    def is_button_disabled(self, ip_address, port_start, port_stop):
    # Sprawdzanie czy pola są puste
        if not ip_address or not port_start or not port_stop:
            return True

        # Sprawdzanie czy adres IP jest poprawny (brak błędu)
        if not self.root.ids.ip_address_input.error:
            return False

        # Jeśli żaden z powyższych warunków nie jest spełniony, przycisk jest zablokowany
        return True 
            
    def check_ip_format(self, text): #sprawdzanie poprawnosci wpisanego adresu ip
        ip_pattern = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'
        )
        if ip_pattern.match(text):
            self.root.ids.ip_address_input.error = False
        else:
            self.root.ids.ip_address_input.error = True
            self.root.ids.ip_address_input.helper_text = "Invalid IP Address"
        
    def build(self):
        return self.screen

Test().run()
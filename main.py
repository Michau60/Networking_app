import re
from kivy.resources import resource_add_path
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
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
import traceroute_adress as ta
import public_ip as pi
import glob
from network_syn_attack import DosAttackThread
from network_ping_of_death import PingOfDeathAttackThread
import json
from kivy.storage.jsonstore import JsonStore
import subprocess
import netifaces
class Network_app(MDApp):
    selected_IF = ""
    auto_refresh_interval = 0 # Co ile sekund ma odświeżać dane
    selected_port_filter = "Show open ports"
    translations = {}
    language = 'Polski'
    theme_style=''
    Theme_primary = ''
    icon_path=""
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path,relative_path)
    
    
    def __init__(self, **kwargs):
        super(Network_app, self).__init__(**kwargs)
        pattern = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'onefile_*')
        self.load_settings()
        matching_folders = glob.glob(pattern)
        if matching_folders:
            # Wybierz pierwszy pasujący folder (lub inny, jeśli jest więcej niż jeden)
            selected_folder = matching_folders[0]
            kv_file_path = os.path.join(selected_folder, 'layout.kv')
            lang_file_path = os.path.join(selected_folder, 'languages.json')
            self.icon_path = os.path.join(selected_folder, 'icon.png')
            self.load_translations(lang_file_path)
            # Załaduj plik .kv
            self.screen = Builder.load_file(kv_file_path)
        else:
            print("Nie znaleziono pasującego folderu TEMP używam lokalnego.")
            current_folder = os.getcwd()
            kv_file_path = os.path.join(current_folder, 'layout.kv')
            lang_file_path = os.path.join(current_folder, 'languages.json')
            self.load_translations(lang_file_path)
            self.screen = Builder.load_file('./layout.kv') #załadowanie interfejsu z pliku
        int_names=inf_stat.interface_data.get_if_names()
        choose = [self.translate("choose","ShowOpenPorts"),self.translate("choose","ShowAll")]
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
        self.port_view_menu.text = self.translate("StringsInCode","ShowOpenPorts")
        self.auto_refresh_event = None  # Zmienna przechowująca zdarzenie zegara
        self.auto_refresh_interval = 1


    def translate(self, section, key):
        # Sprawdź, czy sekcja, klucz i aktualny język są dostępne
        if (
            self.language in self.translations
            and section in self.translations[self.language]
            and key in self.translations[self.language][section]
        ):
            return self.translations[self.language][section][key]
        else:
            # Jeśli tłumaczenie nie jest dostępne, zwróć oryginalny tekst
            return key
    

    def load_translations(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.translations = json.load(file)
    
    
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
        self.screen.ids.selected_if_label.text =self.translate("StringsInCode","SelectedInterface") + text_item
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
        if_name_guid=interface_info.int_info.get_connection_name_from_guid(netifaces.interfaces())
        network_info = interface_info.int_info.get_network_info(inf,if_name_guid)
        try:
            for key,value in network_info.items():
                if value is "None":
                    translated_val = self.translate("InterfaceInformation","noData")
                    network_info[key] = translated_val
        except Exception as e:
            print(e)
        if network_info["Enabled"] == "True":
            translated_val = self.translate("StringsInCode","IfEnabled")
            network_info["Enabled"] = translated_val
        else:
            translated_val = self.translate("StringsInCode","IfDisabled")
            network_info["Enabled"] = translated_val
        self.screen.ids.int_Enabled.text = network_info["Enabled"]
        self.screen.ids.int_IP.text = network_info["IP Address"]
        self.screen.ids.int_MAC.text = network_info["MAC Address"]
        self.screen.ids.int_DNS.text = network_info["DNS Servers"]
        self.screen.ids.int_GW.text = network_info["Default Gateway"]
        self.screen.ids.int_DHCP.text = network_info["DHCP Server"]
        self.screen.ids.int_sub_mask.text = network_info["Subnet Mask"]
    

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
        scanning_label = MDLabel(text=self.translate("StringsInCode","ScanningInProgress"), theme_text_color="Secondary", size_hint_y=None, height=dp(40))
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
        if len(filtered_port_list)==0:
                label = MDLabel(text=self.translate("StringsInCode","NoOpenPorts"), theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                self.root.ids.result_layout.add_widget(label)
        else:
            for result in filtered_port_list:  # przedstawianie wyników w aplikacji
                    label = MDLabel(text=result, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                    self.root.ids.result_layout.add_widget(label)     
    
    
    def domain_info(self, domain):
        self.root.ids.dns_result_layout.clear_widgets()
        domain_info = domain_lookup.domain_info.get_domain_info(domain)
        try:
            for key, value in domain_info.items():
                label_text = f"{key}: {value}"
                label = MDLabel(text=label_text, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                self.root.ids.dns_result_layout.add_widget(label)
        except Exception as e:
                label_text = domain_info
                label = MDLabel(text=label_text, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                self.root.ids.dns_result_layout.add_widget(label)
   
    
    def is_valid_domain_name(self,text): #sprawdzanie poprawnosci nazwy domeny
        domain_pattern = re.compile(r'^(?!:\/\/)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')
        if domain_pattern.match(text):
            self.root.ids.domain_address_input.error = False
            self.root.ids.lookup_button.disabled = False
            self.root.ids.domain_address_input.helper_text = ""
        else:
            self.root.ids.domain_address_input.error = True
            self.root.ids.domain_address_input.helper_text = self.translate("StringsInCode","InvalidDomainAddress")
            self.root.ids.lookup_button.disabled = True
    
           
    def check_ip_format(self,text,field_id,button_id): #sprawdzanie poprawnosci wpisanego adresu ip
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
            ip_address_input.helper_text = self.translate("StringsInCode","InvalidIPAddress")
            self.root.ids[button_id].disabled = True
            

    def check_ports_input(self,text):
        port_start_input = self.root.ids.port_start_input
        port_stop_input = self.root.ids.port_stop_input
        ip_address_input = self.root.ids.port_ip_address_input
        
        ##poprawić
        # start_is_positive=self.check_positive('port_start_input')
        # stop_is_positive=self.check_positive('port_stop_input')
        
        # if start_is_positive==True:
        #     port_start_input.helper_text = ""
        # else:
        #     port_start_input.error=True
        #     port_start_input.helper_text = self.translate("StringsInCode","MustBePositive")
            
        # if stop_is_positive == True and port_stop_input!="":
        #     port_stop_input.helper_text = ""
        # else:
        #     port_stop_input.error=True
        #     port_stop_input.helper_text = self.translate("StringsInCode","MustBePositive")
            # and start_is_positive == True and stop_is_positive == True
        if port_start_input.text !='' and port_stop_input.text!='' and ip_address_input.text!='':
            self.root.ids.scan_port_button.disabled = False
        else:
            self.root.ids.scan_port_button.disabled = True

    def check_positive(self,input_id):
        tb = self.root.ids[input_id]
        is_positive =  re.compile(
                r'\d+$'
            )
        if is_positive.match(tb.text):
            return True
        else:
            return False 
    
    
    def check_fields(self,field1_id,field2_id,button_id):
        field=self.root.ids[field1_id]
        field2=self.root.ids[field2_id]
        button=self.root.ids[button_id]
        if field=="" and field2=="":
            button.disabled=True
        else:
            button.disabled=False
    

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
            self.root.ids.scan_network_button.disabled = False
        else:
            network_input.error = True
            network_input.helper_text_mode = "persistent"
            network_input.helper_text = self.translate("StringsInCode","InvalidNetworkAddressOrMask")
            self.root.ids.scan_network_button.disabled = True
    
    
    def check_domain_format(self, text):
        ip_address_traceroute_input = self.root.ids.traceroute_address_input

        domain_pattern = re.compile(
            r'^(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.?)+[A-Za-z]{2,}\.[A-Za-z]{2,}$'
        )

        if domain_pattern.match(text):
            ip_address_traceroute_input.error = False
            ip_address_traceroute_input.helper_text = ""
            self.root.ids.traceroute_button.disabled = False
        else:
            ip_address_traceroute_input.error = True
            ip_address_traceroute_input.helper_text =self.translate("StringsInCode","InvalidDomainAddress")
            self.root.ids.traceroute_button.disabled = True
    
      
    def scan_network(self, network):
        device_list = self.root.ids.device_list
        device_list.clear_widgets()
        scanning_label = MDLabel(text=self.translate("StringsInCode","ScanningInProgress"), theme_text_color="Secondary", size_hint_y=None, height=dp(40))
        self.root.ids.result_layout_scan.add_widget(scanning_label)

        def callback(scan_results):
            self.root.ids.result_layout_scan.remove_widget(scanning_label)
            for device in scan_results:
                label_text = f"{self.translate('StringsInCode','scan_IP')} {device['ip']}, {self.translate('StringsInCode','scan_HOSTNAME')} {device['hostname']}, {self.translate('StringsInCode','scan_MAC_ADDR')} {device['mac']}"
                label = MDLabel(text=label_text, theme_text_color="Secondary", size_hint_y=None, height=dp(40))
                device_list.add_widget(label)
        def callback_not_installed():
            self.root.ids.result_layout_scan.remove_widget(scanning_label)
            not_installed_label = MDLabel(text=self.translate("StringsInCode","NotInstalledLabel"), theme_text_color="Secondary", size_hint_y=None, height=dp(40))
            not_installed_button = MDRaisedButton(text=self.translate("StringsInCode","NotInstalledButton"), theme_text_color="Secondary", size_hint_y=None, height=dp(40),on_release=self.open_nmap_download_page)
            self.root.ids.result_layout_scan.add_widget(not_installed_label)
            self.root.ids.result_layout_scan.add_widget(not_installed_button)
        t = Thread(target=lambda: self.network_scan_thread(network, callback,callback_not_installed))
        t.start()
        
        
    def open_nmap_download_page(self, *args):
        nmap_download_url = "https://nmap.org/download.html"
        subprocess.Popen(["start", "cmd", "/c", "start", nmap_download_url], shell=True)
        
        
    def is_valid_ip_or_domain(self,input_text,text_filed_id):
        tf=self.root.ids[text_filed_id]
        # Wyrażenie regularne dla poprawnego adresu IP
        ip_pattern = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'
        )

        # Wyrażenie regularne dla poprawnej nazwy domeny z końcówką
        domain_pattern  = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        )

        # Sprawdź, czy to jest poprawny adres IP
        if ip_pattern.match(input_text):
            tf.error = False
            tf.helper_text = ""
            return

        # Sprawdź, czy to jest poprawna nazwa domeny z końcówką
        if domain_pattern.match(input_text):
            tf.error = False
            tf.helper_text = ""
            return
        
        tf.error = True
        tf.helper_text=self.translate("StringsInCode","InvalidIPAddressOrDomain")
           
    
    def get_public_ip(self):
        ip_addr=pi.get_public_ip_from_html()
        self.root.ids.public_ip_label.text = self.translate("StringsInCode","PublicIPAddressLabel") + ip_addr 


    def network_scan_thread(self, network,callback,callback_not_installed):
        if not NetworkDiscover.NetworkScanner.check_nmap_installed():
            Clock.schedule_once(lambda dt: callback_not_installed())     
        else:
            scan_results = NetworkDiscover.NetworkScanner.scan_network(network)
            Clock.schedule_once(lambda dt: callback(scan_results))
        
        
    def start_ping_thread(self,ip_addr,num_ping):
        ping_list = self.root.ids.ping_result_layout
        ping_list.clear_widgets()
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
    
    
    def start_traceroute_thread(self, address):
        traceroute_list = self.root.ids.result_layout_traceroute
        traceroute_list.clear_widgets()

        # Przekazanie adresu jako krotki
        traceroute_thread = Thread(target=self.traceroute_thread, args=(address,))
        traceroute_thread.start()


    def traceroute_thread(self, ip_addr):
        def update_callback(result):
            Clock.schedule_once(lambda dt, r=result: self.update_traceroute_list(r), 0)

        # Zamiana na AddressTraceroute
        ta.AddressTraceroute.traceroute(ip_addr, update_callback)


    def update_traceroute_list(self, result):
        traceroute_list = self.root.ids.result_layout_traceroute
        new_label = MDLabel(text=result)
        traceroute_list.add_widget(new_label)
    
        
    def build(self):
        self.title = "Network APP"
        self.icon = self.icon_path
        self.ping_instance = ap.adress_ping()
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = self.theme_style
        self.theme_cls.primary_palette = self.Theme_primary
        return self.screen
    
    
    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Teal" if self.theme_cls.primary_palette == "Red" else "Red"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        self.theme_style = self.theme_cls.theme_style
        self.Theme_primary = self.theme_cls.primary_palette
        self.save_settings()
    
    
    def toggle_ping_of_death_attack(self):
        target_ip = self.root.ids.pod_ip_address_input.text  
        number_of_packets = self.root.ids.pod_count_input.text 

        if not hasattr(self, 'ping_of_death_thread') or not self.ping_of_death_thread.running:
            self.ping_of_death_thread = PingOfDeathAttackThread(app_instance=self, target_ip=target_ip, number=int(number_of_packets))
            self.ping_of_death_thread.running = True
            self.ping_of_death_thread.start()
            self.root.ids.pod_button.text = self.translate("StringsInCode","AttackInProgress")
            self.root.ids.pod_button.disabled = True
        else:
            self.ping_of_death_thread.running = False
            self.ping_of_death_thread.join()


    def toggle_attack(self):
        ip_addr = self.root.ids.flood_ip_address_input.text
        port = self.root.ids.flood_port_input.text
        if not hasattr(self, 'attack_thread') or not self.attack_thread.running:
            self.attack_thread = DosAttackThread(app_instance=self, ip=ip_addr, port=int(port))
            self.attack_thread.running = True
            self.attack_thread.start()
            self.root.ids.flood_button.text = self.translate("StringsInCode","StopAttack")
        else:
            self.attack_thread.running = False
            self.attack_thread.join()
            self.root.ids.pod_button.text = self.translate("StringsInCode","StartAttack")


    def on_attack_finished(self, *args):
        self.root.ids.pod_button.text = self.translate("StringsInCode","StartAttack")
        self.root.ids.pod_button.disabled = False


    def update_syn_attack_result(self, result):
        self.root.ids.packet_count_label.text = result
        
        
    def update_pod_attack_result(self, result):
        self.root.ids.packet_pod_count_label.text = result
        
        
    def switch_language(self):
        if self.language == 'English':
            self.language = 'Polski'
            self.root.ids.language_label.text=self.translate("Settings","languageText").format(self.language)
        else:
            self.language = 'English'
            self.root.ids.language_label.text=self.translate("Settings","languageText").format(self.language)
        self.restart()
        
        
    def load_settings(self):
        # Domyślne ustawienia
        self.language = 'English'
        self.theme_style = 'Dark'
        self.Theme_primary = 'Teal'
        # Inicjalizacja JsonStore
        subpath ="Network_App_config.json"
        store = JsonStore(os.path.join(os.getenv("LOCALAPPDATA"), subpath))

        # Sprawdzenie, czy klucze istnieją w magazynie
        if store.exists('language'):
            self.language = store.get('language')['value']

        if store.exists('theme'):
            self.theme_style = store.get('theme')['value']
            
        if store.exists('Primary'):
            self.Theme_primary = store.get('Primary')['value']


    def save_settings(self):
        # Inicjalizacja JsonStore
        subpath ="Network_App_config.json"
        store = JsonStore(os.path.join(os.getenv("LOCALAPPDATA"), subpath))

        # Zapisanie ustawień do magazynu
        store.put('language', value=self.language)
        store.put('theme', value=self.theme_style)
        store.put('Primary',value=self.Theme_primary)
        
        
    def restart(self):
        self.save_settings()
        self.root.clear_widgets()
        self.stop()
        self.__init__()
        self.run()
        
        
if __name__ == '__main__':
    try:
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        Network_app().run()
    except Exception as e:
        print(e)
        input("Press enter.")

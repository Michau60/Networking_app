# import packages 
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
import auto_size
import interface_stats as inf_stat
from kivy.clock import Clock
from threading import Thread
import interface_info as inf_info

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


    def interfaces_menu_callback(self, text_item):
        self.screen.ids.selected_if_label.text ="Aktualnie wybrany:" + text_item
        current_interface=text_item
        self.selected_IF = current_interface
        self.packet_data_get_info(current_interface)
        self.get_net_usage_info(current_interface)
        self.get_if_info(current_interface)
        self.menu_if_names.dismiss()
        self.start_auto_refresh()
        
        
    def interval_menu_callback(self, text_item):
        self.auto_refresh_interval = int(text_item)
        self.stop_auto_refresh()
        self.start_auto_refresh()
        self.menu_interval.dismiss()


    def get_if_info(self,inf):
        adapter_guid = inf_info.get_guid_by_interface_name(inf)
        network_info = inf_info.get_network_info(adapter_guid)
        dns_info = inf_info.get_dns_info(inf)
        dhcp_info = inf_info.get_dhcp_info(inf)
        gw_info  = inf_info.get_gw_info(inf)
        self.screen.ids.int_IP.text = str(network_info[0])
        self.screen.ids.int_MAC.text = str(network_info[1])
        self.screen.ids.int_DNS.text = str(dns_info)
        self.screen.ids.int_GW.text = str(gw_info)
        self.screen.ids.int_DHCP.text = str(dhcp_info)
        self.screen.ids.int_sub_mask.text = str(network_info[2])
    

    def packet_data_get_info(self,current_interface):
        interface_packets_values=inf_stat.interface_data.get_packet_interface_data(current_interface)
        self.screen.ids.int_SNT.text = str(interface_packets_values[0])
        self.screen.ids.int_RCV.text = str(interface_packets_values[1])
        self.screen.ids.int_LST_out.text = str(interface_packets_values[2])
        self.screen.ids.int_LST_in.text = str(interface_packets_values[3])
    
    
    def get_net_usage_info(self,current_interface):
        interface_speed_values=inf_stat.interface_data.net_usage(current_interface)
        self.screen.ids.int_speed_out.text = str(interface_speed_values[1])
        self.screen.ids.int_speed_in.text = str(interface_speed_values[0])
        
        
    def build(self):
        return self.screen

Test().run()
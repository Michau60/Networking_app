from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.metrics import dp

import psutil

Builder.load_file("kv/network_usage_app.kv")

class NetworkUsageApp(BoxLayout):
    available_interfaces = []  

    def __init__(self, **kwargs):
        super(NetworkUsageApp, self).__init__(**kwargs)

        self.network_data = {
            "interface": "",
            "bytes_sent": 0,
            "bytes_received": 0,
        }

        self.interface_label = Label(text="Interface: ")
        self.bytes_sent_label = Label(text="Bytes Sent: ")
        self.bytes_received_label = Label(text="Bytes Received: ")

        self.ids.info_layout.add_widget(self.interface_label)
        self.ids.info_layout.add_widget(self.bytes_sent_label)
        self.ids.info_layout.add_widget(self.bytes_received_label)

        self.update_available_interfaces()

    def get_interface_usage(self, selected_interface):
        net_io_counters = psutil.net_io_counters(pernic=True)

        if selected_interface in net_io_counters:
            stats = net_io_counters[selected_interface]
            return {
                "interface": selected_interface,
                "bytes_sent": stats.bytes_sent,
                "bytes_received": stats.bytes_recv,
            }
        else:
            print(f"Brak danych dla interfejsu {selected_interface}.")
            return None

    def update_available_interfaces(self):
        net_io_counters = psutil.net_io_counters(pernic=True)
        self.available_interfaces = list(net_io_counters.keys())
        self.update_spinner()

    def update_and_display_network_usage(self, *args):
        selected_interface = self.ids.interface_spinner.text
        interface_usage_data = self.get_interface_usage(selected_interface)

        if interface_usage_data:
            self.network_data = interface_usage_data
            self.update_labels()

    def update_labels(self):
        self.ids.info_layout.clear_widgets()
        self.ids.info_layout.add_widget(self.interface_label)
        self.ids.info_layout.add_widget(self.bytes_sent_label)
        self.ids.info_layout.add_widget(self.bytes_received_label)

    def display_all_interfaces(self):
        net_io_counters = psutil.net_io_counters(pernic=True)

        if net_io_counters:
            interface_info = ""
            for interface, stats in net_io_counters.items():
                interface_info += f"{interface}: Sent - {stats.bytes_sent}, Received - {stats.bytes_recv}\n"
            self.show_popup("Dostępne interfejsy:", interface_info)
        else:
            self.show_popup("Brak dostępnych interfejsów.")

    def show_popup(self, title, content):
        popup_content = BoxLayout(orientation='vertical', spacing=dp(5), padding=(10, 10))
        label = Label(text=content, size_hint_y=None, height=dp(30 * len(content.split('\n'))), text_size=(400, None), padding=(10, 10))
        button = Button(text='Zamknij', size_hint_y=None, height=dp(40), on_press=lambda x: popup.dismiss())

        popup_content.add_widget(label)
        popup_content.add_widget(button)

        popup = Popup(title=title, content=popup_content, size_hint=(None, None), size=(500, 400))
        popup.open()

    def display_selected_interface(self, selected_interface):
        interface_usage_data = self.get_interface_usage(selected_interface)

        if interface_usage_data:
            self.show_popup(f"Informacje o  {selected_interface}:", f"Sent - {interface_usage_data['bytes_sent']}, Received - {interface_usage_data['bytes_received']}")
        else:
            self.show_popup(f"Brak danych dla interfejsu {selected_interface}.")

    def update_spinner(self):
        self.ids.interface_spinner.values = self.available_interfaces


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(NetworkUsageApp())
        self.add_widget(layout)


class MainScreenManager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        return MainScreenManager()


if __name__ == '__main__':
    MyApp().run()

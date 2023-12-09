from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.lang import Builder

import psutil

Builder.load_file("main.kv")

class NetworkUsageApp(BoxLayout):
    available_interfaces = []

    def __init__(self, **kwargs):
        super(NetworkUsageApp, self).__init__(**kwargs)

        # Przykładowe dane
        self.network_data = {
            "interface": "",
            "bytes_sent": 0,
            "bytes_received": 0,
        }

        # Utwórz etykiety do BoxLayout
        self.interface_label = Label(text="Interface: ")
        self.bytes_sent_label = Label(text="Bytes Sent: ")
        self.bytes_received_label = Label(text="Bytes Received: ")

        self.ids.info_layout.add_widget(self.interface_label)
        self.ids.info_layout.add_widget(self.bytes_sent_label)
        self.ids.info_layout.add_widget(self.bytes_received_label)

        # Pobierz dostępne interfejsy
        self.update_available_interfaces()

        # Uruchom automatyczne odświeżanie co 2 sekundy
        Clock.schedule_interval(self.update_and_display_network_usage, 2)

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
        # Pobierz aktualną listę dostępnych interfejsów
        net_io_counters = psutil.net_io_counters(pernic=True)
        self.available_interfaces = list(net_io_counters.keys())
        self.update_spinner()

    def update_and_display_network_usage(self, *args):
        # Aktualizacja danych o wykorzystaniu interfejsu
        selected_interface = self.ids.interface_spinner.text
        interface_usage_data = self.get_interface_usage(selected_interface)

        if interface_usage_data:
            self.network_data = interface_usage_data
            self.update_labels()

    def update_labels(self):
        # Aktualizacja tekstów etykiet
        self.interface_label.text = "Interface: " + self.network_data["interface"]
        self.bytes_sent_label.text = "Bytes Sent: " + str(self.network_data["bytes_sent"])
        self.bytes_received_label.text = "Bytes Received: " + str(self.network_data["bytes_received"])

    def display_all_interfaces(self):
        # Wyświetl najważniejsze informacje o dostępnych interfejsach
        net_io_counters = psutil.net_io_counters(pernic=True)

        if net_io_counters:
            interface_info = ""
            for interface, stats in net_io_counters.items():
                interface_info += f"{interface}: Sent - {stats.bytes_sent}, Received - {stats.bytes_recv}\n"
            self.show_popup("Dostępne interfejsy:", interface_info)
        else:
            self.show_popup("Brak dostępnych interfejsów.")

    def show_popup(self, title, content):
        # Utwórz Popup z przekazanym tytułem, treścią i przyciskiem
        popup_content = BoxLayout(orientation='vertical', spacing=dp(5), padding=(10, 10))
        label = Label(
            text=content,
            size_hint_y=None,
            height=dp(30 * len(content.split('\n'))),
            text_size=(400, None),
            padding=(10, 10),
        )
        button = Button(text='Zamknij', size_hint_y=None, height=dp(40), on_press=lambda x: popup.dismiss())

        popup_content.add_widget(label)
        popup_content.add_widget(button)

        popup = Popup(title=title, content=popup_content, size_hint=(None, None), size=(500, 400))
        popup.open()

    def display_selected_interface(self, selected_interface):
        # Wyświetl informacje o wybranym interfejsie
        interface_usage_data = self.get_interface_usage(selected_interface)

        if interface_usage_data:
            self.show_popup(
                f"Informacje o  {selected_interface}:",
                f"Sent - {interface_usage_data['bytes_sent']}, Received - {interface_usage_data['bytes_received']}",
            )
        else:
            self.show_popup(f"Brak danych dla interfejsu {selected_interface}.")

    def update_spinner(self):
        # Aktualizuj opcje w spinnerze
        self.ids.interface_spinner.values = self.available_interfaces


class MainView(Screen):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Przycisk, który otwiera boczne menu
        menu_button = Button(text='Menu', size_hint=(None, None), size=(100, 50))
        menu_button.bind(on_release=self.toggle_menu)

        # Boczne menu
        self.side_menu = BoxLayout(orientation='vertical', spacing=5, size_hint=(None, 1), width=150)

        # Dodaj opcje do bocznego menu
        options = ['Widok 1', 'Widok 2', 'Widok 3']
        for option in options:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn, option=option: self.menu_option_selected(option))
            self.side_menu.add_widget(btn)

        layout.add_widget(menu_button)
        layout.add_widget(self.side_menu)

        # Główny obszar aplikacji
        self.network_usage_app = NetworkUsageApp()
        layout.add_widget(self.network_usage_app)

        self.add_widget(layout)

        # Zmienna do śledzenia stanu bocznego menu (ukryte/pokazane)
        self.menu_hidden = True

    def toggle_menu(self, instance):
        # Pokaż lub ukryj boczne menu za pomocą animacji
        animation_duration = 0.3
        if self.menu_hidden:
            Animation(width=150, d=animation_duration, t='out_quad').start(self.side_menu)
        else:
            Animation(width=0, d=animation_duration, t='out_quad').start(self.side_menu)
        self.menu_hidden = not self.menu_hidden

    def menu_option_selected(self, option):
        # W zależności od opcji wybrano odpowiedni widok
        if option == 'Widok 1':
            self.show_view('view1')
        elif option == 'Widok 2':
            self.show_view('view2')
        elif option == 'Widok 3':
            self.show_view('view3')

    def show_view(self, view_name):
        # Przełącz na odpowiedni widok
        if view_name == 'view1':
            self.clear_main_view()
            self.add_widget(self.network_usage_app)
        elif view_name == 'view2':
            self.clear_main_view()
            self.add_widget(Label(text='To jest Widok 2'))
        elif view_name == 'view3':
            self.clear_main_view()
            self.add_widget(Label(text='To jest Widok 3'))

    def clear_main_view(self):
        # Usuń wszystkie widgety z głównego obszaru
        for widget in self.children[:]:
            self.remove_widget(widget)


class NavigationApp(App):
    def build(self):
        sm = ScreenManager()

        # Dodaj główny widok do ScreenManagera
        main_view = MainView(name='main_view')
        sm.add_widget(main_view)

        return sm


if __name__ == '__main__':
    NavigationApp().run()

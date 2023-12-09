# import packages 
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
import psutil
from kivymd.uix.list import OneLineListItem
# writing kv lang 
KV = ''' 
# declaring layout/screen 
MDScreen: 

	# this will create a space navigation bottom 
	MDBottomNavigation: 

		# this will create a navigation button on the bottom of screen 
		MDBottomNavigationItem: 
			name: 'screen 1' 
			text: 'Informacje' 
			icon: 'ethernet' 
			# this will be triggered when screen 1 is selected
			MDBoxLayout:
				orientation: "vertical"
				MDRaisedButton:
					id: select_if_button
					text: "Wybierz interfejs"
					pos_hint: {"center_x": .5, "center_y": .5}
					on_release: app.menu.open()
                MDLabel:
					id: selected_if_label 
					text:"Brak wybranego interfejsu"
                    size_hint_y: None
                    halign: "center"
				MDBoxLayout:
					orientation: "horizontal"
					padding: "100dp"
					MDBoxLayout:
						orientation: "vertical"
						MDLabel:
							text: "Adres IP karty: "
						MDLabel:
							text: "Adres MAC karty: "
						MDLabel:
							text: "Adres serwera DNS: "
						MDLabel:
							text: "Adres bramy: "
						MDLabel:
							text: "Pakiety Wysłane"
						MDLabel:
							text: "Pakiety Odebrane"
						MDLabel:
							text: "Pakiety Utracone" 
					MDBoxLayout:
						orientation: "vertical"
						MDLabel:
                        	id:int_IP
							text: "Brak danych"
						MDLabel:
                        	id:int_MAC
							text: "Brak danych"
						MDLabel:
							id:int_DNS
							text: "Brak danych"
						MDLabel:
							id:int_GW
							text: "Brak danych"
						MDLabel:
							id:int_SNT
							text: "Brak danych"
						MDLabel:
							id:int_RCV
							text: "Brak danych"
						MDLabel:
							id:int_LST
							text: "Brak danych"
				

		# this will create a navigation button on the bottom of screen 
		MDBottomNavigationItem: 
			name: 'screen 2' 
			text: 'Java' 
			icon: 'language-java' 

			# this will be triggered when screen 2 is selected 
			# creates a label 
			MDLabel: 
				text: 'Java' 
				halign: 'center' 

		# this will create a navigation button on the bottom of screen 
		MDBottomNavigationItem: 
			name: 'screen 3' 
			text: 'CPP' 
			icon: 'language-cpp' 

			# this will be triggered when screen 3 is selected 
			# creates a label 
			MDLabel: 
				text: 'CPP' 
				halign: 'center'
		# this will create a navigation button on the bottom of screen 
		MDBottomNavigationItem: 
			name: 'screen 4' 
			text: 'Settings' 
			icon: 'wrench-cog-outline' 

			# this will be triggered when screen 3 is selected 
			# creates a label 
			MDLabel: 
				text: 'CPP' 
				halign: 'center'  
'''
class AutoSizingOneLineListItem(OneLineListItem):
    def __init__(self, **kwargs):
        super(AutoSizingOneLineListItem, self).__init__(**kwargs)
        self.text_size = (self.width, None)
        self.bind(width=lambda instance, width: setattr(instance, 'text_size', (width, None)))

    def adjust_height(self, instance, size):
        instance.height = size[1] / self.line_height + dp(16)  # dp(16) to add some padding

class Test(MDApp):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        if_names=psutil.net_if_addrs().keys()
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "AutoSizingOneLineListItem",
                "on_release": lambda x=f"Wybrany: {i}": self.menu_callback(x),
            } for i in if_names
        ]
        self.menu = MDDropdownMenu(
            caller=self.screen.ids.select_if_button,
            items=menu_items,
            width_mult=4,  # Ustaw szerokość rozwijanej listy, możesz dostosować ten parametr
        )

    def menu_callback(self, text_item):
        self.screen.ids.selected_if_label.text = text_item

    def build(self):
        return self.screen

Test().run()
from kivymd.uix.list import OneLineListItem
from kivy.metrics import dp

class AutoSizingOneLineListItem(OneLineListItem):
    def __init__(self, **kwargs):
        super(AutoSizingOneLineListItem, self).__init__(**kwargs)
        self.text_size = (self.width, None)
        self.bind(width=lambda instance, width: setattr(instance, 'text_size', (width, None)))

    def adjust_height(self, instance, size):
        instance.height = size[1] / self.line_height + dp(16)  # dp(16) to add some padding
        
    def get_max_name_len(names):
        return max(names,key=len)

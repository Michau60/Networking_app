import time
import psutil
class interface_data:
    packet_sent = 0
    packet_recv = 0
    packet_dropin = 0
    packet_dropout = 0
    net_in = 0
    net_out = 0
    def get_if_names():
        if_names=psutil.net_if_addrs().keys()
        return if_names
    
    def get_max_name_len(name):
        return len(max(name, key=len))
    
    def refresh_interface_data(self):
        pass
    
    def net_usage(inf):  
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_1 = net_stat.bytes_recv
        net_out_1 = net_stat.bytes_sent
        time.sleep(1)
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent
        net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
        net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)
        print(f"net_in:{net_in} net_out:{net_out}")
        return net_in,net_out
    
    def get_packet_interface_data(inf):
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        packet_sent = net_stat.packets_sent
        packet_recv = net_stat.packets_recv
        packet_dropin = net_stat.dropin
        packet_dropout = net_stat.dropout
        return packet_sent,packet_recv,packet_dropin,packet_dropout





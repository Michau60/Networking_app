import netifaces
import wmi
#zmodyfikować pobieranie parametrów poprzez wmi a nie netifaces
def get_guid_by_interface_name(interface_name):
    try:
        wmi_obj = wmi.WMI()
        network_config = wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True)

        for config in network_config:
            if interface_name.lower() in config.Description.lower():
                return config.SettingID  # SettingID w Win32_NetworkAdapterConfiguration zawiera GUID

        return None
    except Exception as e:
        print(f"Błąd przy uzyskiwaniu GUID interfejsu: {e}")
        return None

def get_network_info(interface):
    try:
        interfaces = netifaces.interfaces()
        
        # Pobierz informacje o interfejsie
        addrs = netifaces.ifaddresses(interface)

        # Adres IP
        ip_address = addrs[netifaces.AF_INET][0]['addr'] if netifaces.AF_INET in addrs else "Brak danych"

        # Adres MAC
        mac_address = addrs[netifaces.AF_LINK][0]['addr'] if netifaces.AF_LINK in addrs else "Brak danych"

        # Maska podsieci
        subnet_mask = addrs[netifaces.AF_INET][0]['netmask'] if netifaces.AF_INET in addrs else "Brak danych"
        
        return ip_address, mac_address, subnet_mask 
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o interfejsie {interface}: {e}")
        return "Brak danych"
    

def get_dns_info(connection_name):
    c = wmi.WMI()

    # Iteracja przez interfejsy sieciowe
    for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        if connection_name.lower() in interface.Description.lower():
            # Sprawdź, czy istnieje adres DNS
            dns_servers = interface.DNSServerSearchOrder
            if dns_servers:
                return f"{', '.join(dns_servers)}"
            else:
                return "Brak danych"

def get_dhcp_info(connection_name):
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy interfejs korzysta z DHCP
            if interface.DHCPEnabled:
                return interface.DHCPServer
            else:
                "Brak danych"
                
                
def get_gw_info(connection_name):
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy interfejs korzysta z DHCP
            if interface.DefaultIPGateway:
                return interface.DefaultIPGateway[0]
            else:
                "Brak danych"
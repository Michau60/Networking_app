import wmi
import winreg as wr
class int_info:
    def get_connection_name_from_guid(iface_guids):
        iface_names_dict = {guid: '(unknown)' for guid in iface_guids}

        try:
            reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
            reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')

            for guid in iface_guids:
                try:
                    reg_subkey = wr.OpenKey(reg_key, guid + r'\Connection')
                    iface_names_dict[guid] = wr.QueryValueEx(reg_subkey, 'Name')[0]
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"Error: {e}")

        return iface_names_dict

    def get_network_info(connection_name, iface_names_dict):
        c = wmi.WMI()

        # Sprawdź, czy nazwa połączenia istnieje w słowniku
        if connection_name in iface_names_dict.values():
            # Znajdź GUID odpowiadające nazwie połączenia
            guid = next((k for k, v in iface_names_dict.items() if v == connection_name), None)

            # Iteracja przez interfejsy sieciowe
            for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if guid and guid.lower() in interface.SettingID.lower():
                    # Sprawdź, czy istnieje adres IP
                    ip_info = interface.IPAddress[0] if interface.IPAddress else "None"
                    mac_info = interface.MACAddress if interface.MACAddress else "None"
                    subnet_mask = interface.IPSubnet[0] if interface.IPSubnet else "None"
                    dns_servers = ', '.join(interface.DNSServerSearchOrder) if interface.DNSServerSearchOrder else "None"
                    dhcp_info = interface.DHCPServer if interface.DHCPEnabled else "None"
                    gw_info = interface.DefaultIPGateway[0] if interface.DefaultIPGateway else "None"

                    return {
                        'IP Address': ip_info,
                        'MAC Address': mac_info,
                        'Subnet Mask': subnet_mask,
                        'DNS Servers': dns_servers,
                        'DHCP Server': dhcp_info,
                        'Default Gateway': gw_info
                    }

        return {
            'IP Address': "None",
            'MAC Address': "None",
            'Subnet Mask': "None",
            'DNS Servers': "None",
            'DHCP Server': "None",
            'Default Gateway': "None"
        }

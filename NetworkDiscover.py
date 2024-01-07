import nmap
import subprocess
class NetworkScanner:

    def scan_network(ip_range):
        
        try:
            # Uruchom polecenie nmap -v w wierszu poleceń
            result = subprocess.run(['nmap', '-v'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # Sprawdź, czy wynik zawiera informacje o wersji nmap
            if 'Nmap' in result.stdout:
                nm = nmap.PortScanner()
                nm.scan(hosts=ip_range, arguments='-sn')

                devices = []
                for host in nm.all_hosts():
                    hostname = nm[host].hostname() if nm[host].hostname() else 'N/A'
                    if 'mac' in nm[host]['addresses']:
                        mac_address = nm[host]['addresses']['mac']
                    else:
                        mac_address = 'N/A'

                    devices.append({'ip': host,'hostname': hostname, 'mac': mac_address})

                return devices
            else:
                return False

        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Błąd podczas sprawdzania nmap: {e}")
            return False
        
        
        
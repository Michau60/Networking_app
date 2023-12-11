# import socket
# class port_scan:
#     def scan_ports(ip_address,start_port,stop_port):
#         Port_list = []
#         try:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             for port in range(int(start_port),int(stop_port)+1):  
#                 result = sock.connect_ex((ip_address, port))
#                 print (port)
#                 print(result)
#                 if result == 0:
#                      Port_list.append("Port {}: 	 Open".format(port))
#                 else:
#                     Port_list.append("Port {}: 	 Closed".format(port))
#             sock.close()
#             return Port_list
#         except socket.gaierror:
#             return 'Hostname could not be resolved. Exiting'

#         except socket.error:
#             return "Couldn't connect to server"

import socket
from concurrent.futures import ThreadPoolExecutor

class port_scan:
    @staticmethod
    def scan_ports(ip_address, start_port, stop_port, num_threads=10):
        Port_list = []

        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    result = sock.connect_ex((ip_address, port))
                    print(port, result)
                    if result == 0:
                        Port_list.append("Port {}:Open".format(port))
                    else:
                        Port_list.append("Port {}:Closed".format(port))
            except Exception as e:
                Port_list.append("Port {}: Error - {}".format(port, str(e)))

        try:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(scan_port, port) for port in range(int(start_port), int(stop_port) + 1)]

            # Wait for all threads to complete
            for future in futures:
                future.result()

            return Port_list
        except socket.gaierror:
            return 'Hostname could not be resolved. Exiting'
        except socket.error:
            return "Couldn't connect to server"
import subprocess

class adress_ping:
   ip_address = ""
   number_ping = 0
   def ping_ip():
      try:
        result = subprocess.run(['ping', '-n', adress_ping.number_ping, adress_ping.ip_address], capture_output=True, text=True)
        return result.stdout
      except Exception as e:
        return(f"Błąd podczas pingowania: {e}")
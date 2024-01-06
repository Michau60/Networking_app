import subprocess

class adress_ping:
  
    @classmethod
    def ping_ip(cls, ip_addr, ping_num, callback):
        try:
            process = subprocess.Popen(
                ['ping', '-n', str(ping_num), '-w', '1000', ip_addr],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Wywołaj funkcję zwrotną (callback) z wynikiem
                    callback(output.strip())

            # Poczekaj na zakończenie procesu i pobierz ewentualne błędy
            process.wait()
            error_output = process.stderr.read()
            if error_output:
                callback(error_output.strip())

        except Exception as e:
            callback(f"Błąd podczas pingowania: {e}")
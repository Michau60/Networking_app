import subprocess

class adress_ping:
  
    @classmethod
    def ping_ip(cls, ip_addr, ping_num, callback):
        try:
            process = subprocess.Popen(
                ['ping', '-n', str(ping_num), '-w', '1000', ip_addr],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    callback(output.strip())

            process.wait()
            error_output = process.stderr.read()
            if error_output:
                callback(error_output.strip())

        except Exception as e:
            callback(f"Błąd podczas pingowania: {e}")
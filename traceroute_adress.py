import subprocess

class AddressTraceroute:
    @classmethod
    def traceroute(cls, ip_addr, callback):
        try:
            process = subprocess.Popen(
                ['tracert', '-d', ip_addr],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
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
            callback(f"Błąd podczas traceroute: {e}")
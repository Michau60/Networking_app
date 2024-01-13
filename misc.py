class Tools:
    open_port_list = []
    all_port_list = []

    @staticmethod
    def print_list_items(port_list, option):
        open_port_list = []

        if option == "Show open ports" or option=="Pokaż tylko otwarte":
            for result in port_list:
                port_status = result.split(":")[1]
                if port_status == "Open":
                    open_port_list.append(result)
            return open_port_list
        if option == "Show all" or option=="Pokaż wszystkie":
            return port_list

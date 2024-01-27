import whois

class domain_info:
    
    @staticmethod
    def get_domain_info(domain):
            try:
                m_info =  whois.whois(domain) #domain info
                return m_info
            except Exception as e:
                return str(e)
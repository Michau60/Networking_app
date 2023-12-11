import whois
import validators

class domain_info:
    
    @staticmethod
    def get_domain_info(domain):
        if validators.domain(domain): # Check if Domain is Valid
            try:
                m_info =  whois.whois(domain) #domain info
                print(m_info)
                return m_info
            except:
                return f"{domain} is not registered"
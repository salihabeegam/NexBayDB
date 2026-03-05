# config.py - Configuration file for database and email settings

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change this
    'password': '',  # Change this
    'database': 'vessel_db'
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # For Gmail
    'smtp_port': 587,
    'sender_email': 'stores@nxbay.com',  # Change this
    'sender_password': 'vifg glxf wwea owef'  # Use App Password for Gmail
}

# Port Email Mappings with all ports
PORT_EMAIL_MAPPING = {
    # OMAN PORTS
    'Sohar Port - Oman': {
        'portName': 'SOHAR PORT',
        'country': 'OMAN',
        'attachments': ['attachments/OMAN_PORT.xlsx'],
        'subject': 'Ship Supply Services - SOHAR PORT'
    },
    'Salalah Port - Oman': {
        'portName': 'SALALAH PORT',
        'country': 'OMAN',
        'attachments': ['attachments/OMAN_PORT.xlsx'],
        'subject': 'Ship Supply Services - SALALAH PORT'
    },
    'Shinas Port - Oman': {
        'portName': 'SHINAS PORT',
        'country': 'OMAN',
        'attachments': ['attachments/OMAN_PORT.xlsx'],
        'subject': 'Ship Supply Services - MUSCAT PORT'
    },
    'Duqm Port - Oman': {
        'portName': 'DUQM PORT',
        'country': 'OMAN',
        'attachments': ['attachments/OMAN_PORT.xlsx'],
        'subject': 'Ship Supply Services - DUQM PORT'
    },

    # UAE PORTS
    'Jebel Ali Port - UAE': {
        'portName': 'JEBEL ALI PORT',
        'country': 'UAE',
        'attachments': [
            'attachments/UAE_PORT_BOND_PRICE_LIST.xlsx',
            'attachments/UAE_PORT_PROVISION_PRICE_LIST.xlsx',
        ],
        'subject': 'Ship Supply Services - JEBEL ALI PORT'
    },
    'Hamriyah Port - UAE': {
        'portName': 'HAMARIYAH PORT',
        'country': 'UAE',
        'attachments': [
            'attachments/UAE_PORT_BOND_PRICE_LIST.xlsx',
            'attachments/UAE_PORT_PROVISION_PRICE_LIST.xlsx',
        ],
        'subject': 'Ship Supply Services - HAMRIYAH PORT'
    },
    'Fujairah Port - UAE': {
        'portName': 'FUJAIRAH PORT',
        'country': 'UAE',
        'attachments': [
            'attachments/UAE_PORT_BOND_PRICE_LIST.xlsx',
            'attachments/UAE_PORT_PROVISION_PRICE_LIST.xlsx',
        ],
        'subject': 'Ship Supply Services - FUJAIRAH PORT'
    },
    'Abu Dhabi Mina Port - UAE': {
        'portName': 'ABU DHABI MINA PORT',
        'country': 'UAE',
        'attachments': [
            'attachments/UAE_PORT_BOND_PRICE_LIST.xlsx',
            'attachments/UAE_PORT_PROVISION_PRICE_LIST.xlsx',
        ],
        'subject': 'Ship Supply Services - ABU DHABI MINA PORT'
    },
    'Khalifa Port - UAE': {
        'portName': 'KHALIFA PORT',
        'country': 'UAE',
        'attachments': [
            'attachments/UAE_PORT_BOND_PRICE_LIST.xlsx',
            'attachments/UAE_PORT_PROVISION_PRICE_LIST.xlsx',
        ],
        'subject': 'Ship Supply Services - KHALIFA PORT'
    },

    # SAUDI PORTS
    'Jubail Port - Saudi': {
        'portName': 'JUBAIL PORT',
        'country': 'SAUDI ARABIA',
        'attachments': ['attachments/SAUDI_PORT.xlsx'],
        'subject': 'Ship Supply Services - JUBAIL PORT'
    },
    'Jeddah Port - Saudi': {
        'portName': 'RAS AL KHAIR PORT',
        'country': 'SAUDI ARABIA',
        'attachments': ['attachments/SAUDI_PORT.xlsx'],
        'subject': 'Ship Supply Services - JEDDAH PORT'
    },
    'Dammam Port - Saudi': {
        'portName': 'DAMMAM PORT',
        'country': 'SAUDI ARABIA',
        'attachments': ['attachments/SAUDI_PORT.xlsx'],
        'subject': 'Ship Supply Services - DAMMAM PORT'
    }
}


# Helper function to get ports by country
def get_ports_by_country():
    """
    Group ports by country for easier navigation
    Returns a dictionary with country names as keys and list of ports as values
    """
    ports_by_country = {}

    for port_key, port_info in PORT_EMAIL_MAPPING.items():
        country = port_info['country']
        if country not in ports_by_country:
            ports_by_country[country] = []
        ports_by_country[country].append({
            'key': port_key,
            'name': port_info['portName']
        })

    return ports_by_country


# Helper function to get all countries
def get_all_countries():
    """Get list of all unique countries"""
    countries = set()
    for port_info in PORT_EMAIL_MAPPING.values():
        countries.add(port_info['country'])
    return sorted(list(countries))
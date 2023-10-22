import requests
from bs4 import BeautifulSoup

def socks4scrapy(proxy_file, verbose=True):
    url = [
        'https://www.socks-proxy.net/',
    ]
    proxies = []
    for url in url:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if url == 'https://www.socks-proxy.net/':
                table = soup.find('table')
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) > 0:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        country = cols[2].text.strip()
                        uptime = cols[6].text.strip()
                        location = ''
                        if country:
                            location = country.split(',')[0]

                        proxy = {
                            'ip': ip,
                            'port': port,
                            'uptime': uptime,
                            'location': location
                        }
                        proxies.append(proxy)

        except:
            print(f"Error scraping {url}")
    return proxies


def socks4scrapy_no2(proxy_file, verbose=True):
    url = "https://www.proxy-list.download/api/v1/get?type=socks4"
    proxies = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            proxy_list = response.text.split('\r\n')
            for proxy in proxy_list:
                if proxy:
                    ip, port = proxy.split(':')
                    proxy_info = {
                        'ip': ip,
                        'port': port,
                        'uptime': '',
                        'location': ''
                    }
                    proxies.append(proxy_info)
    except Exception as e:
        print(f"Error scraping {url}")
    return proxies


def socks5scrapy(proxy_file, verbose=True):
    url = "https://www.proxy-list.download/api/v1/get?type=socks5"
    proxies = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            proxy_list = response.text.split('\r\n')
            for proxy in proxy_list:
                if proxy:
                    ip, port = proxy.split(':')
                    proxy_info = {
                        'ip': ip,
                        'port': port,
                        'uptime': '',
                        'location': ''
                    }
                    proxies.append(proxy_info)
    except Exception as e:
        print(f"Error scraping {url}")
    return proxies


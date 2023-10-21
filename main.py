import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
import time
import os
import json
import requests
import asyncio
from bs4 import BeautifulSoup
import platform



banner_text = f"""
{Fore.RED}
   ▄▄▄▄▄   ▄███▄   ▄█▄     ▄  █ ▄███▄      ▄  
  █     ▀▄ █▀   ▀  █▀ ▀▄  █   █ █▀   ▀ ▀▄   █ 
▄  ▀▀▀▀▄   ██▄▄    █   ▀  ██▀▀█ ██▄▄     █ ▀  
 ▀▄▄▄▄▀    █▄   ▄▀ █▄  ▄▀ █   █ █▄   ▄▀ ▄ █   
           ▀███▀   ▀███▀     █  ▀███▀  █   ▀▄ 
                            ▀           ▀                                                                                                                 
{Fore.RESET}
"""
banner_bio = f"{Fore.GREEN}Pr0xyHunter V1.0{Fore.RESET}"
banner_server = f"{Fore.GREEN}discord.gg/SecHex{Fore.RESET}"

print(banner_text)
print(banner_bio)
print(banner_server)
init(autoreset=True)
print_lock = threading.Lock()



def set_title(title):
    if platform.system() == "Windows":
        os.system(f"title {title}")
    else:
        print(f"\033]0;{title}\007")

set_title("Pr0xyHunter V1.0")


def scrapyyyyy(proxy_file, verbose):
    urls = [
        'https://www.socks-proxy.net/',
    ]
    proxies = []
    for url in urls:
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




def test_proxy(ip, port, good_proxies):
    try:
        start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, int(port)))
        s.sendall(b"\x04\x01" + int(port).to_bytes(2, byteorder='big') + socket.inet_aton(ip) + b"\x00")
        response = s.recv(8)
        end_time = time.time()
        ping_time = int((end_time - start_time) * 1000)

        if len(response) < 2:
            with print_lock:
                print(f"{Fore.RED}[BAD]{Fore.RESET} {ip}:{port} {Fore.LIGHTRED_EX}Ping:{Fore.RESET} not pingable")
            return

        status = response[1]
        if status == 0x5A:
            with print_lock:
                print(f"{Fore.GREEN}[GOOD]{Fore.RESET} {ip}:{port} {Fore.GREEN}Ping:{Fore.RESET} {Fore.GREEN}{ping_time}ms{Fore.RESET}")
            good_proxies.append(f"{ip}:{port}")
        else:
            with print_lock:
                print(f"{Fore.RED}[BAD]{Fore.RESET} {ip}:{port} {Fore.LIGHTRED_EX}Ping:{Fore.RESET} not pingable")

    except:
        with print_lock:
            print(f"{Fore.RED}[BAD]{Fore.RESET} {ip}:{port} {Fore.LIGHTRED_EX}Ping:{Fore.RESET} not pingable")
    finally:
        s.close()




def discord_webhook(txt_filename, webhook_url):
    files = {'file': (txt_filename, open(txt_filename, 'rb'), 'text/plain')}
    response = requests.post(webhook_url, files=files)



    if response.status_code == 200:
        print(f"proxys '{txt_filename}' sent to Discord successfully!")
    else:
        print(f"Failed to send TXT file to Discord. Status Code: {response.status_code}")




async def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        webhook_url = config.get('webhook_url', '')
        num_threads = config.get('num_threads', 5)
        proxy_file = config.get('proxy_file')
        proxy_scraper = config.get('proxy_scraper', False)
        restart_interval = config.get('restart_interval', None)

        await asyncio.sleep(4)

    if not webhook_url:
        print("Webhook URL is missing in config.json.")
        return

    while True:
        if proxy_scraper:
            proxies = scrapyyyyy(proxy_file, verbose=True)

            with open(proxy_file, 'w') as f:
                for proxy in proxies:
                    f.write(f"{proxy['ip']}:{proxy['port']}\n")

        file_name = proxy_file

        with open(file_name, 'r') as f:
            proxies = f.readlines()

        good_proxies = []

        if num_threads == 1:
            for proxy in proxies:
                ip, port = proxy.strip().split(':')
                test_proxy(ip, port, good_proxies)
        else:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for proxy in proxies:
                    ip, port = proxy.strip().split(':')
                    executor.submit(test_proxy, ip, port, good_proxies)

        with open("good_proxies.txt", 'w') as f:
            for proxy in good_proxies:
                f.write(proxy + "\n")
        discord_webhook("good_proxies.txt", webhook_url)

        if restart_interval:
            print(f"Rebooting in {restart_interval} seconds...")
            await asyncio.sleep(restart_interval)
        else:
            print("Exiting...")
            break

if __name__ == "__main__":
    asyncio.run(main())

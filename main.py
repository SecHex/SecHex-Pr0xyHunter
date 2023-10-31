import socket
import threading
import os
import json
import requests
import asyncio
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
from discord_webhook import DiscordWebhook, DiscordEmbed

from functions.scrapybacky import socks5scrapy, socks4scrapy, socks4scrapy_no2



banner_text = f"""
{Fore.RED}
⠀⠀⢀⣤⣶⣶⣤⣄⡀
⠀⢀⣿⣿⣿⣿⣿⣿⣿⡆       
⠀⠸⣿⣿⣿⣿⣿⡟⡟⡗      
⠀⠀⠙⠏⠯⠛⣉⢲⣧⠟  
⠀⠀⠠⢭⣝⣾⠿⣴⣿⠇     discord.gg/SecHex
⠀⠀⢐⣺⡿⠁⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣶⣶⣶⣶⣶⣶⠀
⠀⠀⣚⣿⠃ ⣶⣶⣶⣶
⢀⣿⣿⣿⣷⢒⣢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣶⣶⣄⠄
⢰⣿⣿⡿⣿⣦⠬⢝⡄⠀⠀⠀⠀⠀⠀⢠⣿⠿⠿⠟⠛⠋⠁
⠠⢿⣿⣷⠺⣿⣗⠒⠜⡄⠀⠀⠀⠀⣴⠟⠁
⠀⣰⣿⣷⣍⡛⣯⣯⣙⡁⠀⠀⣠⡾⠁
⠀⠨⢽⣿⣷⢍⣛⣶⢷⣼⣠⣾⠋
⠀⠀⠘⢿⣿⣖⠬⣹⣶⣿⠟⠁
⠀⠀⠀⠚⠿⠿⡒⠨⠛⠋
⠀⠀⠀⠐⢒⣛⣷
⠀⠀⠀⢘⣻⣭⣭
⠀⠀⠀⡰⢚⣺⣿
⠀⠀⢠⣿⣿⣿⣿⣦⡄
⠀⠀⢸⡿⢿⣿⢿⡿⠃
⠀⠀⠘⡇⣸⣿⣿⣿⣆                                                                                                   
{Fore.RESET}
"""
banner_bio = f"{Fore.GREEN}Pr0xyHunter V1.1{Fore.RESET}"
banner_server = f"{Fore.GREEN}discord.gg/SecHex{Fore.RESET}"

print(banner_text)
print(banner_bio)
print(banner_server)
init(autoreset=True)
print_lock = threading.Lock()
timer_thread_stop = threading.Event()

def set_title(title):
    if platform.system() == "Windows":
        os.system(f"title {title}")
    else:
        print(f"\033]0;{title}\007")

set_title("Pr0xyHunter V1.1")





def test_proxy(ip, port, good_proxies):
    current_thread = threading.current_thread().name 
    thread_identifier = f"{Fore.LIGHTCYAN_EX}Thread: {current_thread[-1]}{Fore.RESET}" 

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
                print(f"{thread_identifier} | {Fore.RED}[BAD]{Fore.RESET} | {ip}:{port} | {Fore.LIGHTRED_EX}Ping: 404{Fore.RESET}")
            return

        status = response[1]
        if status == 0x5A:
            with print_lock:
                print(f"{thread_identifier} | {Fore.GREEN}[GOOD]{Fore.RESET} | {ip}:{port} | {Fore.GREEN}Ping: {ping_time}ms{Fore.RESET}")
            good_proxies.append(f"{ip}:{port}")
        else:
            with print_lock:
                print(f"{thread_identifier} | {Fore.RED}[BAD]{Fore.RESET} | {ip}:{port} | {Fore.LIGHTRED_EX}Ping: 404{Fore.RESET}")

    except:
        with print_lock:
            print(f"{thread_identifier} | {Fore.RED}[BAD]{Fore.RESET} | {ip}:{port} | {Fore.LIGHTRED_EX}Ping: 404{Fore.RESET}")
    finally:
        s.close()



def discord_webhook(txt_filename, webhook_url, message=None):
    files = {'file': (txt_filename, open(txt_filename, 'rb'), 'text/plain')}

    if message:
        data = {'content': message}
    else:
        data = {}

    response = requests.post(webhook_url, files=files, data=data)

    if response.status_code == 200:
        print(f"proxys '{txt_filename}' sent to Discord successfully!")
    else:
        print(f"Failed to send TXT file to Discord. Status Code: {response.status_code}")


def count_active_threads():
    global previous_thread_count
    while True:
        num_active_threads = threading.active_count()
        if num_active_threads != previous_thread_count:
            print(f"{Fore.LIGHTCYAN_EX}Active Threads:{Fore.RESET} {num_active_threads}")
            previous_thread_count = num_active_threads
        time.sleep(5)




async def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        webhook_url = config.get('webhook_url', '')
        num_threads = config.get('num_threads', 5)
        proxy_file = config.get('proxy_file')
        proxy_scraper = config.get('proxy_scraper', False)
        restart_interval = config.get('restart_interval', None)
        active_threads_enabled = config.get('thread_logs', True)


        if active_threads_enabled:
            active_thread_checker = threading.Thread(target=count_active_threads)
            active_thread_checker.daemon = True
            active_thread_checker.start()

        await asyncio.sleep(4)

    if not webhook_url:
        print("Webhook URL is missing in config.json.")
        return

    start_time = time.time()

    while True:
        if proxy_scraper:
            proxies_socks4 = socks4scrapy(proxy_file)
            proxies_socks4_no2 = socks4scrapy_no2(proxy_file)
            proxies_socks5 = socks5scrapy(proxy_file)
            proxies = proxies_socks4 + proxies_socks4_no2 + proxies_socks5

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
                    num_threads_used = num_threads

        with open("good_proxies.txt", 'w') as f:
            for proxy in good_proxies:
                f.write(proxy + "\n")


        num_good_proxies = len(good_proxies)
        scan_duration = time.time() - start_time

        embed = DiscordEmbed(title="SecHex-Pr0xyHunter V1.1", color=16777215)
        embed.set_description(
            f"Found **{num_good_proxies}** good proxies in **{scan_duration:.2f}** seconds using **{num_threads_used}** threads\n[SecHex-Pr0xyHunter](https://github.com/SecHex/SecHex-Pr0xyHunter)")

        webhook = DiscordWebhook(url=webhook_url)
        webhook.add_embed(embed)
        webhook.execute()

        discord_webhook("good_proxies.txt", webhook_url)

        if restart_interval:
            print(f"Rebooting in {restart_interval} seconds...")
            await asyncio.sleep(restart_interval)
        else:
            print("Exiting...")





if __name__ == "__main__":
    asyncio.run(main())

'''
Created on 18.04.2014

@author: Tobias Ruck
'''

import requests
import re

proxies = [ ]

def read_proxies(path):
    text = open("proxies.txt").read()
    regex = re.compile("(\d*\.\d*\.\d*\.\d*)\s+(\d*)")
    for match in regex.finditer(text):
        proxies.append("http://%s:%s" % (match.group(1), match.group(2)))
    regex = re.compile("(\d*\.\d*\.\d*\.\d*:\d*)")
    for match in regex.finditer(text):
        proxies.append("http://%s" % (match.group(0)))

def test_proxy(proxy_url, timeout=0.1):
    session = requests.Session()
    session.proxies = { "http": proxy_url, "https": proxy_url }
    try:
        response = session.get("http://google.com", timeout=timeout)
        if response.status_code != 200:
            #print(proxy, "response error", response)
            return False
        #print(proxy_url, "works")
        return True
    except:
        #print(proxy_url, "doesnt work")
        return False

if __name__ == '__main__':
    read_proxies("proxies.txt")
    print(proxies)
    #proxies = ["http://94.23.244.96:3128"]
    for proxy in proxies:
        if test_proxy(proxy):
            print(proxy)
    
    
    
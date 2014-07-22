'''
Created on 18.04.2014

@author: Tobias Ruck
'''

import requests
import re
import os
import http.server

proxies = [ ]

os.environ['HTTP_PROXY'] = ''

def read_proxies(path):
    text = open(path).read()
    regex = re.compile("(\d*\.\d*\.\d*\.\d*)\s+(\d*)")
    for match in regex.finditer(text):
        proxies.append("http://%s:%s" % (match.group(1), match.group(2)))
    regex = re.compile("(\d*\.\d*\.\d*\.\d*:\d*)")
    for match in regex.finditer(text):
        proxies.append("http://%s" % (match.group(0)))

def test_proxy(proxy_url, timeout=0.4):
    session = requests.Session()
    session.proxies = { "http": proxy_url, "https": proxy_url }
    try:
        response = session.get("http://google.com", timeout=timeout)
        if response.status_code != 200:
            #print(proxy, "response error", response)
            return False
        if 'title="Google"' not in response.text:
            return False
        #print(proxy_url, "works")
        return True
    except Exception as e:
        #print(proxy_url, "doesnt work")
        #print(e)
        return False

if __name__ == '__main__':
    #read_proxies("proxy_lists/proxies4.txt")
    read_proxies("tested_proxies.txt")
    #proxies = ["http://94.23.244.96:3128"]
    for proxy in proxies:
        if test_proxy(proxy):
            print(proxy)
    
    
    
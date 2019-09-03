import os
import re
from threading import Thread
from queue import Queue
import json
import requests

def sherlock_main (username):
    urls=[]
    data_file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data.json')
    site_data=json.load(open(data_file_path,'r'))
    concurrent=len(site_data)
    all_dict=[]
    results_total={}
    for social_network, net_info in site_data.items():
        results_site = {}
        results_site['url_main'] = net_info.get("urlMain")
        regex_check = net_info.get("regexCheck")
        if regex_check and re.search(regex_check, username) is None:
            results_site["exists"] = "illegal"
            results_site["url_user"] = ""
            results_site['http_status'] = ""
            results_site['response_text'] = ""
            results_site['response_time_ms'] = ""
            net_info['res']=None            
        else:
            url = net_info["url"].format(username)
            results_site["url_user"] = url
            url_probe = net_info.get("urlProbe")
            if url_probe is None:
                 net_info['url']=url
            else :
                 net_info['url']=url_probe.format(username)
            if social_network != "GitHub":
                if net_info["errorType"] == 'status_code':
                      pass 
            if net_info["errorType"] == "response_url":
                net_info['allow_redirects'] = False
            else:
                net_info['allow_redirects'] = True
            results_total[social_network] = results_site
    return results_total


import os
import re
from threading import Thread
from queue import Queue
import json
import requests

def doWork(q):
    while True:
        netinfo = q.get()
        res = getStatus(netinfo)
        netinfo['res']=res
        q.task_done()
def getStatus(netinfo):
    try:
        res=requests.get(netinfo['url'],timeout=2,allow_redirects=netinfo['allow_redirects'])
        if (res.status_code):
            return res
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        pass
    return None


def sherlock_main (username):
    urls=[]
    data_file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data.json')
    site_data=json.load(open(data_file_path,'r'))
    concurrent=len(site_data)
    q = Queue(concurrent * 2)
    all_dict=[]
    results_total={}
    for i in range(concurrent):
        t = Thread(target=doWork,args=(q,))
        t.daemon = True
        t.start()
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
            q.put(net_info)
    q.join()
    all_result=[]
    for social_network,net_info in site_data.items():
        error_type = net_info["errorType"]
        http_status = "?"
        response_text = ""
        r = net_info['res']
        error_type=net_info['errorType']
        try:
            http_status = r.status_code
        except:
            continue
            pass
        try:
            response_text = r.text.encode(r.encoding)
        except:
            pass
        if error_type == "message":
            error = net_info.get("errorMsg")
            if not error in r.text:
                all_result.append(results_total[social_network].get('url_user'))
            else:
                pass
        elif error_type == "status_code":
            if not r.status_code >= 300 or r.status_code < 200:
                all_result.append(results_total[social_network].get('url_user'))
            else:
                pass
        elif error_type == "response_url":
            if 200 <= r.status_code < 300:
                all_result.append(results_total[social_network].get('url_user'))
            else:
                pass
        elif error_type == "":
            exists = "error"
    return all_result


#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""
import json
import os
import re
import sys
import random
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from concurrent.futures import ThreadPoolExecutor
from time import time
import requests
from requests_futures.sessions import FuturesSession

class ElapsedFuturesSession(FuturesSession):
    def request(self, method, url, hooks={}, *args, **kwargs):
        start = time()
        def timing(r, *args, **kwargs):
            elapsed_sec = time() - start
            r.elapsed = round(elapsed_sec * 1000)
        try:
            if isinstance(hooks['response'], (list, tuple)):
                # needs to be first so we don't time other hooks execution
                hooks['response'].insert(0, timing)
            else:
                hooks['response'] = [timing, hooks['response']]
        except KeyError:
            hooks['response'] = timing
        return super(ElapsedFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)

def format_response_time(response_time, verbose):
    return " [{} ms]".format(response_time) if verbose else ""


def get_response(request_future, error_type, social_network, verbose=False, retry_no=None):
    try:
        rsp = request_future.result()
        if rsp.status_code:
            return rsp, error_type, rsp.elapsed
    except requests.exceptions.HTTPError as errh:
        pass
    except requests.exceptions.ConnectionError as errc:
        pass
    except requests.exceptions.Timeout as errt:
        pass
    except requests.exceptions.RequestException as err:
        pass
    return None, "", -1

def sherlock(username, site_data, verbose=False, tor=False, unique_tor=False, proxy=None, print_found_only=False):
    amount =0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    executor = ThreadPoolExecutor(max_workers=len(site_data))
    underlying_session = requests.session()
    underlying_request = requests.Request()
    session = ElapsedFuturesSession(
        executor=executor, session=underlying_session)
    results_total = {}
    for social_network, net_info in site_data.items():
        # return data get line
        results_site = {}
        results_site['url_main'] = net_info.get("urlMain")
        regex_check = net_info.get("regexCheck")
        if regex_check and re.search(regex_check, username) is None:
            results_site["exists"] = "illegal"
            results_site["url_user"] = ""
            results_site['http_status'] = ""
            results_site['response_text'] = ""
            results_site['response_time_ms'] = ""
        else:
            url = net_info["url"].format(username)
            results_site["url_user"] = url
            url_probe = net_info.get("urlProbe")
            if url_probe is None:
                url_probe = url
            else:
                url_probe = url_probe.format(username)
            request_method = session.get
            if social_network != "GitHub":
                if net_info["errorType"] == 'status_code':
                    request_method = session.head
            if net_info["errorType"] == "response_url":
                allow_redirects = False
            else:
                allow_redirects = True
            if 1:
                future = request_method(url=url_probe, headers=headers,
                                        allow_redirects=allow_redirects
                                        )
            net_info["request_future"] = future
            #print (future)
            if unique_tor:
                underlying_request.reset_identity()

        results_total[social_network] = results_site
    for social_network, net_info in site_data.items():
        results_site = results_total.get(social_network)
        url = results_site.get("url_user")
        exists = results_site.get("exists")
        if exists is not None:
            continue
        error_type = net_info["errorType"]
        http_status = "?"
        response_text = ""
        future = net_info["request_future"]
        r, error_type, response_time = get_response(request_future=future,
                                                    error_type=error_type,
                                                    social_network=social_network,
                                                    verbose=verbose,
                                                    retry_no=3)
        try:
            http_status = r.status_code
        except:
            pass
        try:
            response_text = r.text.encode(r.encoding)
        except:
            pass

        if error_type == "message":
            error = net_info.get("errorMsg")
            if not error in r.text:
                exists = "yes"
                amount = amount+1
            else:
                if not print_found_only:
                    pass
                exists = "no"
        elif error_type == "status_code":
            if not r.status_code >= 300 or r.status_code < 200:
                exists = "yes"
                amount = amount+1
            else:
                if not print_found_only:
                    pass
                exists = "no"
        elif error_type == "response_url":
            if 200 <= r.status_code < 300:
                exists = "yes"
                amount = amount+1
            else:
                if not print_found_only:
                    pass
                exists = "no"
        elif error_type == "":
            if not print_found_only:
                pass
            exists = "error"
        results_site['exists'] = exists
        results_site['http_status'] = http_status
        results_site['response_text'] = response_text
        results_site['response_time_ms'] = response_time

        results_total[social_network] = results_site
    return results_total


def sherlock_main(username):
    version_string='1'
    response_json_online = None
    site_data_all = None
    data_file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data.json')
    if site_data_all is None:
        if not os.path.exists(data_file_path):
            print("JSON file at doesn't exist.")
            print(
                "If this is not a file but a website, make sure you have appended http:// or https://.")
            sys.exit(1)
        else:
            raw = open(data_file_path, "r", encoding="utf-8")
            try:
                site_data_all = json.load(raw)
            except:
                print("Invalid JSON loaded from file.")
    site_data = site_data_all
    
    return_result=[]
    if username:
        results = {}
        start=time()
        results = sherlock(username, site_data, verbose='',
                           tor='', unique_tor='', proxy='', print_found_only='')
        end=time()
        print (end-start)
        for website_name in results: 
            dictionary = results[website_name]
            if dictionary.get("exists") == "yes":
                return_result.append(dictionary["url_user"])
    print (return_result)
    return (return_result)

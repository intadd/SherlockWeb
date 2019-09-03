from __future__ import absolute_import
from celery import shared_task
import requests
import os
import re
import json
from fake_useragent import UserAgent

@shared_task
def sherlock_main (result):
        error_type = result.get("errorType")
        http_status = "?"
        response_text = ""
        try:
            ua = UserAgent()
            headers={'User-Agent':ua.random}
            r=requests.get(result.get('url'),headers=headers,timeout=5,allow_redirects=result.get('allow_redirects'))
            if (r.status_code):
                pass
        except requests.exceptions.Timeout:
            return ('NO','timeout')
        except Exception as e:
            return ('NO',str(e))

        error_type=result.get('errorType')
        try:
            http_status = r.status_code
        except:
            return('NO','test1')
            pass
        try:
            response_text = r.text.encode(r.encoding)
        except:
            pass
        if error_type == "message":
            error = result.get("errorMsg")
            if not error in r.text:
                return('MOK',result.get('url_user'))
            else:
                pass
        elif error_type == "status_code":
            if not r.status_code >= 300 or r.status_code < 200:
                return('SOK',result.get('url_user'))
            else:
                pass
        elif error_type == "response_url":
            if 200 <= r.status_code < 300:
                return('ROK',result.get('url_user'))
            else:
                pass
        elif error_type == "":
            exists = "error"
        return('NO','NOT attach')

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .tools.googleimage.googleimage import GETimage
from .tasks import sherlock_main
from celery.result import AsyncResult
import os
import re
import json


def index(request):
    return render(request, 'main/index.html', {})


def report(request):
    username = request.GET.get("username", False)
    if (username):
        images, source = GETimage(username)
        data_file_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data.json')

        site_data = json.load(open(data_file_path, 'r'))

        results_total = {}

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
                net_info['res'] = None
            else:
                url = net_info["url"].format(username)
                results_site["url_user"] = url
                url_probe = net_info.get("urlProbe")
                if url_probe is None:
                    net_info['url'] = url
                else:
                    net_info['url'] = url_probe.format(username)
                if social_network != "GitHub":
                    if net_info["errorType"] == 'status_code':
                        pass
                if net_info["errorType"] == "response_url":
                    net_info['allow_redirects'] = False
                else:
                    net_info['allow_redirects'] = True
                results_total[social_network] = results_site
                results_total[social_network].update(net_info)
        tasks_id = []

        for info in results_total:
            if(results_total[info].get('exists') != 'illegal'):
                try:
                    ids = sherlock_main.delay(results_total[info])
                    tasks_id.append(ids.id)
                except Exception as e:
                    print(e)
        return render(request, 'main/report.html', {'aaa': tasks_id, 'bbb': images, 'ccc': source})
    else:
        return render(request, 'main/report.html', {})


def sherlock_api(request):
    tasks_key = request.GET.get('key', '')
    if (tasks_key):
        res = AsyncResult(tasks_key, app=sherlock_main)
        if(res.status == 'SUCCESS'):
            datas = res.get()
            urls = datas[1]
            if(res.status != 'NO'):
                urls = urls.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(
                    '(', '&#40;').replace('"', '&quot').replace('\'', '&#x27').replace('\\', '&#x2F').replace(')', '&#41;')
            data = {'code': datas[0], 'url': urls}
            return JsonResponse(data, safe=False)

    return JsonResponse({'code': 'Yet', 'url': ''}, safe=False)


# Create your views here.

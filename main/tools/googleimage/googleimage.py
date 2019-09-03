    

from bs4 import BeautifulSoup

import requests

def GETimage(username):

    site_list=[]

    releate=[]
    url_info = "https://www.google.com/search?"
    params = {
        "q" : username,
        "tbm":"isch"
    }
    params_sub = {
	"q" : "@"+username,
	"tbm":"isch"
    }
    html_object = requests.get(url_info,params) #html_object html source 값
    html_object_sub=requests.get(url_info,params_sub)
    if html_object.status_code == 200 and html_object_sub.status_code == 200:
        bs_object = BeautifulSoup(html_object.text,"html.parser")
        bs_object_sub=BeautifulSoup(html_object_sub.text,"html.parser")
        img_data = bs_object.find_all("img")
        img_data_sub = bs_object_sub.find_all("img")
        for i in (img_data[1:]):
            site_list.append(i['src'])
        for i in (img_data_sub[1:]):
            releate.append(i['src'])
    return (site_list,releate)

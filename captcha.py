import requests
import time
import sys
import os

sitekey='f7de0da3-3303-44e8-ab48-fa32ff8ccc7b'
curl='https://2captcha.com/demo/hcaptcha'
api_key = os.getenv("api_key")

try:
    url = "https://2captcha.com/in.php?key="+api_key+"&method=hcaptcha&sitekey="+sitekey+"&pageurl="+curl
    r = requests.get(url).content.decode().split("|")
    print(r)
    if len(r) > 1:
        ID = r[1]
        time.sleep(10)
        url = "https://2captcha.com/in.php?key="+api_key+"&action=get&id="+ID
        r = requests.get(url).content
        print(r)
except Exception as e:
    sys.exit(e)

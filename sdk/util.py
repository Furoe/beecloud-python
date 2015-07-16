import urllib2
import ssl
import json
def httpGet(url):
    try:
        gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        f = urllib2.urlopen(url, context = gcontext)
        s = f.read()
        return True, s
    except :
        try:
            f = urllib2.urlopen(url)
            s = f.read()
            return True, s
        except:
            return False, None

def httpPost(url, data):
    try:
        req = urllib2.Request(url=url, data=data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        return json.loads(res) 
    except:
        r = {}
        r['result_code'] = 14
        r['result_msg'] = 'RUN_TIME_ERROR'
        return r

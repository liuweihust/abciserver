import argparse
import urllib
import urllib2
import base64
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument('--file', default='templ.json', type=str, help='file to send')
parser.add_argument('--server', default='127.0.0.1', type=str, help='server address')
parser.add_argument('--port', default=26657, type=int, help='server port')

def builddata(data):
    data = base64.b64encode(data)

    dic={}
    dic["jsonrpc"]="2.0"
    dic["id"]="anything"
    dic["method"]="broadcast_tx_commit"
    TX={}
    TX["tx"]=data
    dic["params"]=TX
    urldata = json.dumps(dic)
    return urldata

def postdata(data,server="127.0.0.1",port=26657):
    requrl = "http://%s:%d"%(server,port)
    req = urllib2.Request(url = requrl,data =data)
    print(req)

    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print(res)

if __name__ == '__main__':
    args = parser.parse_args()
    #parser.parse_args()
    with open(args.file, 'rb') as f:
        data = f.read()  # produces single string
        f.close()

    urldata = builddata(data)
    postdata(data=urldata,server=args.server,port=args.port)


import argparse
import urllib
import urllib2
import base64
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument('--file', default='../examples/templ_all.json', type=str, help='file to send')
parser.add_argument('--keypath', default='prvkey.json', type=str, help='private key file to read')
parser.add_argument('--server', default='127.0.0.1', type=str, help='server address')
parser.add_argument('--port', default=26657, type=int, help='server port')

def builddata(data):
    dic={}
    dic["jsonrpc"]="2.0"
    dic["id"]="anything"
    dic["method"]="broadcast_tx_commit"
    TX={}
    TX["tx"]=data
    dic["params"]=TX
    urldata = json.dumps(dic)
    return urldata

def getoutput(cmd):
    #out = os.popen("./mycrypto -cmd "+cmd).read()
    runcmd="./mycrypto -cmd "+cmd
    out = os.popen("./mycrypto -cmd "+cmd).read()
    return out

def signdata(data,keyfile):
    sender = getoutput("id")
    #data = base64.b64encode(data)
    print("in signdata:",data)
    sign = getoutput("sign -msg "+data)
    print("signdata=",sign)
    
    dic={}
    dic["sender"]=sender
    dic["data"]=data
    dic["sig"]=sign
    urldata = json.dumps(dic)
    return urldata

def postdata(data,server="127.0.0.1",port=26657):
    requrl = "http://%s:%d"%(server,port)
    req = urllib2.Request(url = requrl,data =data)

    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print(res)

if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.file, 'rb') as f:
        data = f.read()  # produces single string
        f.close()

    #Clean data with the \r\n and spaces
    ddic = json.loads(data) 
    data = json.dumps(ddic)
    print("rawdata=",data)

    signdata = signdata(data=data,keyfile=args.keypath)
    print("after sig:",signdata)
    b64data = base64.b64encode(signdata)
    print("after b64:",signdata)
    urldata = builddata(b64data)
    print("final data:",urldata)
    postdata(data=urldata,server=args.server,port=args.port)



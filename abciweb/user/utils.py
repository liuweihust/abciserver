from __future__ import absolute_import
import os
import subprocess
from user.models import ABCIUser
import re
import urllib
import json
from urllib import request

CryptoBinFile="crypto"
DataBinFile="getdata"
PostDataBinFile="postdata"
DefaultKeyPath='./static/'

def Execute(BinFile,CMD):
    execcmd = BinFile + CMD
    o = os.popen(execcmd).read()
    return o
    #p = subprocess.Popen(execcmd, shell=True, stdout=subprocess.PIPE)
    #return p.communicate()

def CryptoExec(CMD):
    return Execute(CryptoBinFile,CMD)

def DataExec(CMD):
    return Execute(DataBinFile,CMD)

def GetPubkey(user,keypath=None):
    if keypath is None:
        keypath = DefaultKeyPath
    cmd = ' -mode pub -key '+ keypath + user + '-prv.json'
    return CryptoExec(cmd)

def GeneratePrvkey(user,keypath=None):
    if keypath is None:
        keypath = DefaultKeyPath
    cmd = " -mode key -key " + keypath + user + '-prv.json'
    return CryptoExec(cmd)

def adduser(user):
    path = GeneratePrvkey(user)
    pub = GetPubkey(user)

    u1 = ABCIUser(username=user, prvkey_file=path, pubkey=pub)
    u1.save()

def postdata(path,prvkey_file,server="127.0.0.1",port=26657):
    cmd = ' -key ' + prvkey_file + ' -file ' + path + ' -server ' + server + ' -port ' + str(port)
    return Execute(PostDataBinFile,cmd)

def pubencode(plain,pubkey):
    cmd = ' -mode pubenc -plain ' + plain + ' -pubkey ' + pubkey
    return CryptoExec(cmd)

def postcipherdata(path,prvkey_file,pubkey,server="127.0.0.1",port=26657):
    cmd = ' -key ' + prvkey_file + ' -cipher symm -file ' + path + ' -server ' + server + ' -port ' + str(port)
    o = Execute(PostDataBinFile,cmd)
    res = re.search(r'^Secret:.*', o)
    find = res.group()
    if (len(find)) == 0:
        print("Can't find secret:%s" % o)
        return None
    split = find.split(":", 1)
    return pubencode(split[1],pubkey),split[1]

def query(type,id='',server='127.0.0.1',port=26657):
    """
    if id != '':
        url = "http://"+server+":"+str(port)+"/tx_search?query=\"type='"+type + "'\""
    """

    url = "http://" + server + ":" + str(port) + "/tx_search?query=\"type='" + type + "'\""
    print("url=%s" % url)
    data = request.urlopen(url).read()
    decode = data.decode('UTF-8')
    print("out=%s"%decode)

    qdict = json.loads(decode)
    rawarray = []
    for item in qdict['result']['txs']:
        rawarray.append(item)
    return rawarray


if __name__ == '__main__':
    out = Execute(CryptoBinFile," -mode pub")
    print("default pub:%s"%out)

    sellerpub = GetPubkey('seller')
    print("seller's pub:%s"%sellerpub)

    err = postdata("../../examples/prvkey.json","../../examples/prvkey.json")
    print("err=",err)

    secret = postcipherdata("../../examples/prvkey.json", "../../examples/prvkey.json",'029e1c91ff4c7e64530c275f58dbb5602a486d44b8f32d44299ebb20574117a785')
    print("secret=", secret)

    query('template','')
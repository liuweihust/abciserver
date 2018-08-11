from __future__ import absolute_import
import os
import subprocess
from user.models import ABCIUser
import re
import urllib
import json
from urllib import request
import base64

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

def postdata(path,user,server="127.0.0.1",port=26657):
    prvkey_file = os.path.join(DefaultKeyPath,user + '-prv.json')
    cmd = ' -key ' + prvkey_file + ' -file ' + path + ' -server ' + server + ' -port ' + str(port)
    return Execute(PostDataBinFile,cmd)

def pubencode(plain,pubkey):
    cmd = ' -mode pubenc -plain ' + plain + ' -pubkey ' + pubkey
    return CryptoExec(cmd)

def postcipherdata(path,user,pubkey,server="127.0.0.1",port=26657):
    prvkey_file = os.path.join(DefaultKeyPath, user + '-prv.json')
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
    decodearray = []
    for item in qdict['result']['txs']:
        ddict = {}
        for td in item['tx_result']['tags']:
            key = base64.b64decode(td['key']).decode('utf-8')
            value = base64.b64decode(td['value']).decode('utf-8')
            ddict[str(key)] = value

        if len(id) != 0:
            if type == 'template':
                if id != ddict['tid']:
                    continue
            elif type == 'data':
                if id != ddict['did']:
                    continue
            elif type == 'contract':
                if id != ddict['cid']:
                    continue
            elif type == 'transaction':
                if id != ddict['sid']:
                    continue
            else:
                continue

        ddict['tx'] = json.loads(base64.b64decode(item['tx']).decode('utf-8'))
        decodearray.append(ddict)
        rawarray.append(item)
    return rawarray,decodearray

def DecipherPubEncodedstr(key,cipher):
    cmd=CryptoBinFile + " -mode prvdec -key " + key + " -cipher " + cipher
    print(cmd)
    o=os.popen(cmd).read()
    if o[0:7] != "Error:":
        return o
    else:
        return None

def DecipherSymmEncodedstr(symmkey,cipher):
    cmd=CryptoBinFile + " -mode symmdec -secret " + symmkey + " -cipher " + cipher
    o=os.popen(cmd).read()
    if o[0:7] != "Error:":
        return o
    else:
        return None

def Decipher(cipher,encrypedkey,user):
    prvkey_file = os.path.join(DefaultKeyPath, user + '-prv.json')
    plainkey = DecipherPubEncodedstr(prvkey_file,encrypedkey)
    if plainkey is None:
        return None
    return DecipherSymmEncodedstr(plainkey,cipher)

if __name__ == '__main__':
    out = Execute(CryptoBinFile," -mode pub")
    print("default pub:%s"%out)

    sellerpub = GetPubkey('seller')
    print("seller's pub:%s"%sellerpub)

    err = postdata("seller","../../examples/prvkey.json")
    print("err=",err)

    secret = postcipherdata("../../examples/prvkey.json", "seller",'029e1c91ff4c7e64530c275f58dbb5602a486d44b8f32d44299ebb20574117a785')
    print("secret=", secret)

    query('template','')
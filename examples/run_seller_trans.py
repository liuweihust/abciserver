#!/usr/bin/env 
import os
import json  
import tempfile
import re

FilePath="./"
DataFiles=["data_general.json","data_smoke.json","data_bloodnormal.json"]
DataAll="data_all.json"
TransData="trans.json"
PostBinFile="postdata"
CryptoBinFile="crypto"
BuyerPrvFile="buyer_prvkey.json"
SellerPrvFile="seller_prvkey.json"

#Get Seller's pubkey
cmd=CryptoBinFile + " -mode pub -key " + BuyerPrvFile
print("seller pubkey cmd:%s\n",cmd)
seller=os.popen(cmd).read()
seller_utf8 = u'%s'%seller

#Send Seller's data and collect encode keys
detepat = re.compile('^Secret:.*$')
pubenc_keys=[]
for item in DataFiles:
    cmd=PostBinFile + " -file " + FilePath+item + " -cipher symm"
    print("c=encipher cmd:%s\n"%(cmd))
    o=os.popen(cmd).read()
    res = re.search(r'^Secret:.*',o) 
    find = res.group()
    if (len(find)) == 0:
        print("Can't find secret:%s"%o)
        break
    split = find.split(":", 1)
    cmd=CryptoBinFile + " -mode pubenc -pubkey " + seller_utf8 + " -plain " + split[1]
    print("encipher symm key cmd:%s\n"%(cmd))
    o=os.popen(cmd).read()
    keyenc_utf8 = u'%s'%o
    pubenc_keys.append(keyenc_utf8)
    print("pubenc out:%s"%o)

print("enckeys=",pubenc_keys)

#Send assenmble data
cmd=PostBinFile + " -file " + FilePath+DataAll
o=os.popen(cmd).read()
print("assemble data:%s"%o)

with open(FilePath+TransData, 'r') as f:  
    data = json.loads(f.read())  
    for i in range(len(pubenc_keys)):
        data['keys'][i]['key']=pubenc_keys[i]
    f.close()


tmpfile = tempfile.mkstemp()
print("temp file:%s"%(tmpfile[1]))
jsonstr=json.dumps(data)
with open(tmpfile[1], 'w') as f:  
    f.write(jsonstr)
    f.close()

cmd=PostBinFile + " -file " + tmpfile[1] + " -cipher plain"
o=os.popen(cmd).read()
print(o)

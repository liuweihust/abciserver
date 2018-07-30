#!/usr/bin/env 
import os
import json  
import tempfile
import re

FilePath="./"
DataFiles=["data_general.json","data_bloodnormal.json","data_smoke.json"]
DataAll="data_all.json"
TransData="trans.json"
BinFile="postdata"
BuyerPrvFile="buyer_prvkey.json"
SellerPrvFile="seller_prvkey.json"

#Get Seller's pubkey
cmd=BinFile + " -mode pub -key " + SellerPrvFile
seller=os.popen(cmd).read()
seller_utf8 = u'%s'%seller

#Send Seller's data and collect encode keys
detepat = re.compile('^Secret:.*$')
pubenc_keys=[]
for item in DataFiles:
    cmd=BinFile + " -file " + FilePath+item + " -cipher symm"
    o=os.popen(cmd).read()
    res = re.search(r'^Secret:.*',o) 
    find = res.group()
    if (len(find)) == 0:
        print("Can't find secret:%s"%o)
        break
    split = find.split(":", 1)
    cmd=BinFile + " -mode pubenc -pubkey \"" + seller_utf8 + "\" -plain " + split[1]
    print("cmd:%s\n"%(cmd))
    o=os.popen(cmd).read()
    keyenc_utf8 = u'%s'%o
    pubenc_keys.append(keyenc_utf8)

print("enckeys=",pubenc_keys)

#Send assenmble data
cmd=BinFile + " -file " + FilePath+DataAll
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

cmd=BinFile + " -file " + tmpfile[1] + " -cipher plain"
o=os.popen(cmd).read()
print(o)

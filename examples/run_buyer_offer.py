#!/usr/bin/env 
import os
import json  
import tempfile

FilePath="./"
TemplFiles=["templ_bloodnormal.json","templ_general.json","templ_smoke.json","templ_all.json"]
OfferData="offer.json"
BinFile="postdata"
BuyerPrvFile="buyer_prvkey.json"
SellerPrvFile="seller_prvkey.json"

for item in TemplFiles:
    cmd=BinFile + " -file " + FilePath+item + " -cipher plain"
    print("cmd:%s\n"%(cmd))
    o=os.popen(cmd).read()
    print(o)

cmd=BinFile + " -mode pub -key " + BuyerPrvFile
buyer=os.popen(cmd).read()
buyer_utf8 = u'%s'%buyer

cmd=BinFile + " -mode pub -key " + SellerPrvFile
seller=os.popen(cmd).read()
seller_utf8 = u'%s'%seller

with open(FilePath+OfferData, 'r') as f:  
    data = json.loads(f.read())  
    data['from']=buyer_utf8
    data['to']=seller_utf8
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

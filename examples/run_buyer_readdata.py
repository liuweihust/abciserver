#!/usr/bin/env 
import os
import json  
import tempfile
import base64
import operator

FilePath="./"
BinFile="getdata"
BuyerPrvFile="buyer_prvkey.json"

def ParseJsonRpc(o):
    data = json.loads(o)
    if data.has_key("result"):
        num_offer=data["result"]["total_count"]
    else:
        print("no transaction found\n")
        return None

    tags=[]
    txs=[]
    for i in range(len(data["result"]["txs"])):
        txs.append(data["result"]["txs"][i]['tx'])

        tag={}
        for j in range(len(data["result"]["txs"][i]['tx_result']['tags'])):
            key=data["result"]["txs"][i]['tx_result']['tags'][j]["key"]
            value=data["result"]["txs"][i]['tx_result']['tags'][j]["value"]
            deckey = base64.b64decode(key)
            decvalue = base64.b64decode(value)
            tag[deckey]=decvalue
        tags.append(tag)

    return tags,txs

def ParseSigData(sigstr):
    b64_decode = base64.b64decode(sigstr)
    sigdata=json.loads(b64_decode)
    sigkeys=["sender","sig","data"]
    for key in sigkeys:
        if not sigdata.has_key(key):
            return None,None,None
    
    return sigdata[ sigkeys[0] ], sigdata[ sigkeys[1] ], sigdata[ sigkeys[2] ]

def CheckSig(sender,sig,data):
    #Fixme: add check sig process later
    return True


def QueryData(lurl):
    cmd=BinFile + " -lurl " + lurl 
    o=os.popen(cmd).read()
    return o

#Search transaction
def QueryTrans(sid=None):
    #cmd=BinFile + " -lurl \"tx_search?query=\\\"type='transaction'\\\"&prove=true\""
    if sid is None:
        return QueryData("\"tx_search?query=\\\"type='transaction'\\\"\"")
    else:
        #FIXME: add query criteria later
        return QueryData("\"tx_search?query=\\\"type='transaction'\\\"\"")

def QueryDID(DID):
    o = QueryData("\"tx_search?query=\\\"did='%s'\\\"\""%DID)
    tags,payloads = ParsePayload(o)
    alldata=None
    for i in range(len(tags)):
        if tags[i].has_key('type'):
            if tags[i]['type'] == 'data':
                alldata = payloads[i]
                return alldata
        else:
            print("Wrong tags:",i,tags)
            exit(1)

def QueryTID(TID):
    o=QueryData("\"tx_search?query=\\\"tid='%s'\\\"\""%TID)
    tags,payloads = ParsePayload(o)
    alldata=None
    for i in range(len(tags)):
        if tags[i].has_key('type'):
            if tags[i]['type'] == 'template':
                alldata = payloads[i]
                return alldata
        else:
            print("Wrong tags:",i,tags)
            return None

def ParsePayload(o):
    #Parse jsonrpc resp to trans dict
    tags,txs = ParseJsonRpc(o)
    if txs is None:
        print("Parse JSON RPC rsp error:%s\n"%o)
        return None,None,None

    payloads=[]

    #parse sender,sig and payload data
    for i in range(len(txs)):
        sender,sig,payload = ParseSigData(txs[i])
        if sender is None:
            print("Parse sigdata error\n",txs[i])
            return None,None,None

        match = CheckSig(sender,sig,payload)
        if not match:
            print("Check sigdata error\n")
            return None,None,None

        payloads.append(payload)

    return tags,payloads

def GetDataList(alldata):
    array = alldata['data']
    newdict = {}
    for item in array:
        k=item['DID']
        v=item['value']
        newdict[k]=v

    sorted_x = sorted(newdict.iterkeys())

    datalist = {}
    for key in sorted_x:
        datalist[key] = newdict[key]
    return datalist

if __name__ == '__main__':
    #1. Query trans
    o=QueryTrans()
    tags,payloads = ParsePayload(o)
    if len(payloads)==0:
        print("Parse error\n")

    #We assume the first trans is to be query
    did = payloads[0]['did'] #mean data ID
    keys = payloads[0]['keys']
    cid = payloads[0]['cid'] #means contract ID
    sid = payloads[0]['sid'] #means transaction ID
    print("keys",keys)
   
    #2. Query assembly data with did
    alldata=QueryDID(did)
    if alldata['encode'] != 'plain':
        print("Error:Wrong assembly encode mode:%s\n"%alldata['encode'])
        exit(2)

    #3. Get all data's DID:dids in array datalist, order by 'DID'
    didlist = GetDataList(alldata)
    print("didlist",didlist)

    #4. Query all data in assembly data
    cipherdata = []
    tids = []
    for v in didlist.values():
        cipher=QueryDID(v)
        cipherdata.append(cipher)
    print("cipherdata",cipherdata)

    #5. Query data related templates
    temps = []
    for cdata in cipherdata:
        if cdata.has_key('tid'):
            temp=QueryTID(cdata['tid'])
            if temp is None:
                print("can fetch template:%s\n"%cdata['tid'])
                exit(3)
            temps.append(temp)
        else:
            print("cipherdata has no tid",cdata,"\n")
            exit(4)
    print("templates:",temps)


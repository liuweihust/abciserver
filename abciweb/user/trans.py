from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
import json
from user.models import DataTemplate,Data,Transaction,Offer
import uuid
from user import utils

BASE_DIR="./static/"

def trans(request):
    #return HttpResponse("hello")
    user = request.session.get('username', None)
    pubkey = request.session.get('pubkey', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user
    buyer = ''

    if request.method == 'POST':
        transtr = request.POST['trans']
        data_all = json.loads(transtr)

        # build transaction dict
        transdic = {}
        transdic['type'] = "transaction"
        transdic['sid'] = str(uuid.uuid1())
        transdic['cid'] = data_all.pop('cid')
        transdic['did'] = data_all['did']
        buyer = data_all.pop('buyer')
        transdic['keys'] = []

        for item in data_all['data']:
            path = item.pop('path')
            #FIXME: send path data here
            encsecret,secret = utils.postcipherdata(path,user,buyer)
            transdic['keys'].append({"DID":item['DID'],"Encode":"receiverpubkey,aes,sha1","key":encsecret})

            #Save data to DB
            with open(path, 'r') as f:
                tdata = json.loads(f.read())
                mdata = Data(did=tdata['did'],tid=tdata['tid'],encode='symm',path=path,owner=pubkey,key=secret)
                mdata.save()
                f.close()

        datastr = json.dumps(data_all)
        context['dataall'] = datastr
        jsonstr = json.dumps(data_all)
        dapath = os.path.join(BASE_DIR,data_all['did']+'.json')
        with open(dapath, 'w') as f:
            f.write(jsonstr)
            f.close()

        #Send data_all file, plain
            utils.postdata(dapath, user)

        mdata = Data(did=data_all['did'],tid=data_all['tid'],encode='plain',path=dapath)
        mdata.save()

        #Send it and save it to db
        transtr = json.dumps(transdic)
        context['trans'] = transtr
        tranpath = os.path.join(BASE_DIR, transdic['sid'] + '.json')
        with open(tranpath, 'w') as f:
            f.write(transtr)
            f.close()
            utils.postdata(tranpath, user)

        mtrans = Transaction(sid=transdic['sid'],did=transdic['did'],cid=transdic['cid'],path=tranpath)
        mtrans.save()

    trans=[]
    selltrans=[]
    btrans = Transaction.objects.all()
    for tran in btrans:
        qoffers = Offer.objects.all().filter(cid=tran.cid)
        for offer in qoffers:
            if offer.seller == pubkey:
                selltrans.append([tran.sid,offer.cid,offer.tid,tran.did,tran.time,tran.path])
            elif offer.buyer == pubkey:
                trans.append([tran.sid,offer.cid,offer.tid,tran.did,tran.time,tran.path])

    context['trans'] = trans
    context['selltrans'] = selltrans
    return render(request, "trans.html", context)


def newtrans(request):
    # return HttpResponse("hello")
    user = request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user
    if 'Accept' in request.GET:
        context['cid'] = request.GET['Accept']
        data_all = {}
        data_all['type'] = 'data'
        data_all['encode'] = 'plain'
        data_all['tid'] = ''
        data_all['did'] = ''
        data_all['data'] = []
    else:
        context['cid'] = request.POST['cid']
        data_all = json.loads(request.POST['trans'])

    with open(os.path.join(BASE_DIR,context['cid']+'.json'),'r') as f:
        data = json.loads(f.read())
        context['seller'] = data['to']
        context['buyer'] = data['from']
        context['fee'] = data['fee']
        context['tid'] = data['tid']
        data_all['tid'] = data['tid']
        data_all['cid'] = data['cid']
        #Will be remove later, to store buyer' pub key for trans
        data_all['buyer'] = data['from']
        if data_all['did'] == '':
            data_all['did'] = str(uuid.uuid1())
        f.close()

    tmpl = DataTemplate.objects.get(tid=context['tid'])
    tids = []
    with open(tmpl.path,'r') as f:
        tdata = json.loads(f.read())
        for item in tdata['template']:
            ntmpl = DataTemplate.objects.get(tid=item['tid'])
            didindex = item['DID']

            if request.method == 'POST':
                obj = request.FILES.get(str(didindex))
                if obj is None:
                    path = ''
                    for dataitem in data_all['data']:
                        if dataitem['DID'] == didindex:
                            path = dataitem['path']
                    tids.append([didindex, item['tid'], ntmpl.path, path])
                    #tids.append([didindex, item['tid'], ntmpl.path, ''])
                else:
                    path = os.path.join(BASE_DIR, obj.name)
                    with open(path, 'wb') as f:
                        for chunk in obj.chunks():
                            f.write(chunk)
                        f.close()

                    with open(path, 'r') as f:
                        ndata = json.loads(f.read())
                        f.close()

                    ndict = {}
                    ndict['DID'] = didindex
                    ndict['value'] = ndata['did']
                    ndict['path'] = path
                    data_all['data'].append(ndict)

                    tids.append([didindex, item['tid'], ntmpl.path, obj.name])
            else:
                tids.append( [ didindex,item['tid'], ntmpl.path,'' ] )

        f.close()
    context['subtids'] = tids
    jsonstr = json.dumps(data_all)
    context['datall'] = jsonstr

    return render(request, "newtrans.html", context)

def viewdata(request):
    user = request.session.get('username', None)
    pubkey = request.session.get('pubkey', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user

    if 'sid' not in request.GET:
        return render(request, "trans.html", context)

    mtran = Transaction.objects.get(sid=request.GET['sid'])
    with open(mtran.path, 'r') as f:
        sdata = json.loads(f.read())
        f.close()

    moffer = Offer.objects.get(cid=mtran.cid)
    with open(moffer.path, 'r') as f:
        cdata = json.loads(f.read())
        f.close()

    mtmpl = DataTemplate.objects.get(tid=moffer.tid)
    with open(mtmpl.path, 'r') as f:
        tdata = json.loads(f.read())
        f.close()

    for i in range(len(tdata['template'])):
        pass

    mdataall = Data.objects.get(did=mtran.did)
    with open(mdataall.path, 'r') as f:
        dadata = json.loads(f.read())
        f.close()

    dataarray = []
    tmplplainarray = []
    for i in range(len(dadata['data'])):
        #Fetch data
        did = dadata['data'][i]['value']
        _,subcipher = utils.query('data',did)
        dataarray.append(subcipher[0]['tx']['data'])
        encodedkey = None

        tplid = None
        for j in range(len(tdata['template'])):
            if tdata['template'][j]['DID'] == dadata['data'][i]['DID']:
                tplid = DataTemplate.objects.get(tid=tdata['template'][j]['tid'])
                break

        if tplid is None:
            print("TPL ID not found:%s\n"%tdata['template'][j]['DID']['tid'])

        with open(tplid.path, 'r') as f:
            tpldata = json.loads(f.read())
            f.close()

        for j in range(len(sdata)):
            if sdata['keys'][j]['DID'] == dadata['data'][i]['DID']:
                encodedkey = sdata['keys'][j]['key']
                break

        plain = utils.Decipher( subcipher[0]['tx']['data']['data'] ,encodedkey, user)
        tmplplainarray.append([plain,json.dumps(tpldata['template'])])

    """
    context['trans'] = json.dumps(sdata)
    context['offer'] = json.dumps(cdata)
    context['dadata'] = json.dumps(dadata)
    context['dataarray'] = json.dumps(dataarray)
    context['tmplplainarray'] = json.dumps(tmplplainarray)
    context['tmpls'] = json.dumps(plainarray)
    """

    context['sid'] = request.GET['sid']
    context['cid'] = sdata['cid']
    context['tid'] = moffer.tid
    context['did'] = sdata['did']
    context['Time'] = mtran.time
    context['seller'] = cdata['to']
    context['buyer'] = cdata['from']
    context['spath'] = mtran.path
    context['cpath'] = moffer.path
    context['tpath'] = mtmpl.path
    context['dpath'] = mdataall.path
    context['tmplplainarray'] = tmplplainarray

    return render(request, "getdata.html", context)
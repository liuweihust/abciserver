from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
import json
from user.models import DataTemplate,Data,Transaction
import uuid
from user.utils import postdata,postcipherdata

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
        transdic['cid'] = data_all['tid']
        transdic['did'] = data_all['did']
        buyer = data_all.pop('buyer')
        transdic['keys'] = []

        for item in data_all['data']:
            path = item.pop('path')
            #FIXME: send path data here
            encsecret,secret = postcipherdata(path,os.path.join(BASE_DIR, user + '.json'),buyer)
            transdic['keys'].append({"DID":item['DID'],"Encode":"receiverpubkey,aes,sha1","key":encsecret})

            #Save data to DB
            with open(path, 'r') as f:
                tdata = json.loads(f.read())
                mdata = Data(did=tdata['did'],tid=tdata['tid'],encode='symm',path=path,owner=pubkey,key=secret)
                mdata.save()

        datastr = json.dumps(data_all)
        context['dataall'] = datastr
        jsonstr = json.dumps(data_all)
        dapath = os.path.join(BASE_DIR,data_all['did']+'.json')
        with open(dapath, 'w') as f:
            f.write(jsonstr)
            f.close()

        #Send data_all file, plain
        postdata(dapath, os.path.join(BASE_DIR, user + '.json'))

        mdata = Data(did=data_all['did'],tid=data_all['tid'],encode='plain',path=dapath)
        mdata.save()

        #Send it and save it to db
        transtr = json.dumps(transdic)
        context['trans'] = transtr
        tranpath = os.path.join(BASE_DIR, transdic['sid'] + '.json')
        with open(tranpath, 'w') as f:
            f.write(transtr)
            f.close()
        postdata(tranpath, os.path.join(BASE_DIR, user + '.json'))

        mtrans = Transaction(sid=transdic['sid'],did=transdic['did'],cid=transdic['cid'])
        mtrans.save()
        """
        cmd = CryptoBinFile + " -mode key -key " + BuyerPrvFile
        os.popen(cmd).read()
        logging.debug("genkey cmd=%s\n" % (cmd))
        context['comments'] = "Generate ok"
        """

    """    
    cmd = CryptoBinFile + " -mode pub -key " + BuyerPrvFile
    context['keydata'] = os.popen(cmd).read()
    logging.debug("buyer cmd=%s\n,keydata=%s" % (cmd,context['keydata']))
    """
    
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


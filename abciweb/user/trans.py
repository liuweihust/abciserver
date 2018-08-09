from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
import json
from user.models import DataTemplate
BASE_DIR="./static/"

def trans(request):
    #return HttpResponse("hello")
    user = request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user
    """
    if request.POST:
        cmd = CryptoBinFile + " -mode key -key " + BuyerPrvFile
        os.popen(cmd).read()
        logging.debug("genkey cmd=%s\n" % (cmd))
        context['comments'] = "Generate ok"

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

    with open(os.path.join(BASE_DIR,context['cid']+'.json'),'r') as f:
        data = json.loads(f.read())
        context['seller'] = data['to']
        context['buyer'] = data['from']
        context['fee'] = data['fee']
        context['tid'] = data['tid']
        f.close()

    tmpl = DataTemplate.objects.get(tid=context['tid'])
    tids = []
    with open(tmpl.path,'r') as f:
        tdata = json.loads(f.read())
        for item in tdata['template']:
            ntmpl = DataTemplate.objects.get(tid=item['tid'])
            tids.append( [ item['tid'], ntmpl.path ] )
        f.close()
    context['subtids'] = tids

    """
    if request.POST:
        cmd = CryptoBinFile + " -mode key -key " + BuyerPrvFile
        os.popen(cmd).read()
        logging.debug("genkey cmd=%s\n" % (cmd))
        context['comments'] = "Generate ok"

    cmd = CryptoBinFile + " -mode pub -key " + BuyerPrvFile
    context['keydata'] = os.popen(cmd).read()
    logging.debug("buyer cmd=%s\n,keydata=%s" % (cmd,context['keydata']))
    """

    return render(request, "newtrans.html", context)


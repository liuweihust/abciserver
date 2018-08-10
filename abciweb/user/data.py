from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
from user.models import Data,DataTemplate

def data(request):
    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')
    pubkey = request.session['pubkey']

    context = {}
    context['username'] = user

    data = Data.objects.all().filter(owner=pubkey)
    adata = []
    for item in data:
        #info.append([item.tname,item.category,item.sender,item.path])
        tmpl = DataTemplate.objects.get(tid=item.tid)
        adata.append([item.did, item.path, item.tid,tmpl.path,item.time])
    context['data'] = adata

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

    return render(request, "data.html", context)


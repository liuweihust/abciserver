from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.conf import settings
from django.http import HttpResponseRedirect
from user import utils
from user.models import ABCIUser

CryptoBinFile="crypto"
BuyerPrvFile="buyer_prvkey.json"
SellerPrvFile="seller_prvkey.json"

def global_setting(request):
    return {
        'USER': settings.USER,
        'PUBKEY': settings.PUBKEY,
    }

def gui(request):
    #return HttpResponse("hello")
    context = {}
    context['name'] = 'Hello World!'
    return render(request, 'index.html', context)

def user(request):
    #return HttpResponse("hello")
    cat = request.path.split('/')
    logging.debug("buyer path=%s" % (request.path))

    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    queryuser = ABCIUser.objects.get(username=user)


    context = {}
    context['username'] = user

    if request.POST:
        path = utils.GeneratePrvkey(context['username'])
        pub = utils.GetPubkey(context['username'])
        queryuser.prvkey_file = path
        queryuser.pubkey = pub
        queryuser.save()
        context['comments'] = "Generate ok"


    context['keydata'] = utils.GetPubkey(context['username'])

    return render(request, "user.html", context)

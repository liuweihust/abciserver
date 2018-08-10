from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
from user.models import ABCIUser,DataTemplate,Offer
import uuid
import json
from user.utils import postdata

BASE_DIR="./static/"

def buildoffer(buyer,seller,fee,tid,cid=None):
    offer = {}
    offer['to'] = seller
    offer['from'] = buyer
    if cid is None:
        offer['cid'] = str(uuid.uuid1())
    else:
        offer['cid'] = cid
    offer['fee'] = fee
    offer['tid'] = tid
    offer['encode'] = 'plain'
    offer['type'] = 'contract'

    path = os.path.join(BASE_DIR,offer['cid']+".json")
    jsonstr = json.dumps(offer)
    with open(path, 'w') as f:
        f.write(jsonstr)
        f.close()
    return path,offer['cid']


def offer(request):
    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user

    #Handle new offer req
    if request.POST:
        buyer = request.POST['buyer']
        seller = request.POST['seller']
        fee = request.POST['fee']
        tid = request.POST['tid']

        path, cid = buildoffer(buyer, seller, fee, tid=tid)
        # FIXME: do send transaction here
        postdata(path, os.path.join(BASE_DIR, user + '.json'))

        noffer = Offer(cid=cid,seller=seller,buyer=buyer,tid=tid,fee=int(fee),path=path)
        noffer.save()

    #Prepare data for my provided offers
    info = []
    offers = Offer.objects.all().filter(buyer=request.session['pubkey'])

    for item in offers:
        info.append([item.cid, item.time, item.seller, item.fee,item.path])
    context['offers'] = info

    #Prepare data for my received offers
    recvs = []
    recoffers = Offer.objects.all().filter(seller=request.session['pubkey'])
    for item in recoffers:
        recvs.append([item.cid, item.time, item.seller, item.fee, item.path])
    context['received'] = recvs

    return render(request, "offer.html", context)

def newoffer(request):
    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user

    #Prepare my preuploaded templates to choose
    tmpldata = []
    tmpls = DataTemplate.objects.all().filter(sender=user)
    for item in tmpls:
        tmpldata.append([item.tid,item.tname])
    context['tmpls'] =  tmpldata

    #Prepare users to be choose as receiver
    userdata = []
    users = ABCIUser.objects.all()
    for item in users:
        if item.username != user:
            userdata.append([item.username,item.pubkey])
    context['sellers'] = userdata

    #default fee, changable
    context['fee'] = 5
    context['buyer'] = request.session.get('pubkey', None)
    return render(request, "newoffer.html", context)
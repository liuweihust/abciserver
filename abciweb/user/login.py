#from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import logging
import os
from user import utils
#from .user import User
from user.models import ABCIUser

def loginform(request):
    #utils.adduser('seller')
    #utils.adduser('buyer')

    context = {}
    return render(request, 'login.html', context)

def auth(request):
    context = {}
    if request.POST:
        context['username'] = request.POST['username']
        context['password'] = request.POST['password']


    request.session['username'] = request.POST['username']
    queryuser = ABCIUser.objects.get(username=context['username'])

    request.session['pubkey'] = queryuser.pubkey

    """
    if not finduser:
        return render(request, 'login.html', context)
    """

    logging.debug("user:%s,pwd:%s"%(context['username'],context['password']))
    #return render(request, 'user.html', context)
    return HttpResponseRedirect('/user.html')

def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

#from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import logging
import os
#from .user import User
from user.models import ABCIUser
 
def inituser():
    u1 = ABCIUser(username='seller')
    u1.save()

    u2 = ABCIUser(username='buyer')
    u2.save()

def loginform(request):
    #inituser()

    context = {}
    return render(request, 'login.html', context)

def auth(request):
    context = {}
    if request.POST:
        context['username'] = request.POST['username']
        context['password'] = request.POST['password']


    request.session['username'] = request.POST['username']
    logging.debug("user:%s,pwd:%s"%(context['username'],context['password']))
    #return render(request, 'user.html', context)
    return HttpResponseRedirect('/user.html')

def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect

def offer(request):
    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user
    context['time'] = "Aug 1st 2018 17:49:34"
    context['sender'] = "6h8y08u9issasf"
    context['tmpl'] = "wfesdfwd"
    context['fee'] = 50
    return render(request, "offer.html", context)


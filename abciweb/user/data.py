from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect

def data(request):
    user =  request.session.get('username', None)
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

    return render(request, "data.html", context)


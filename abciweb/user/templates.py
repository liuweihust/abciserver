from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
from user.models import DataTemplate
import json

BASE_DIR="/tmp/"

def template(request):
    #return HttpResponse("hello")
    cat = request.path.split('/')
    logging.debug("buyer path=%s" % (request.path))

    user = request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    if request.method == 'POST':
        obj = request.FILES.get('filename')
        if obj is not None:
            path = os.path.join(BASE_DIR, obj.name)
            f = open(path, 'wb')
            for chunk in obj.chunks():
             f.write(chunk)
            f.close()

            valid=True
            with open(path, 'r') as f:
                data = json.loads(f.read())
                if not 'tid' in data:
                    context['comments'] = 'Err:tid not found'
                    valid = False
                if not 'tname' in data:
                    context['comments'] = 'Err:tname not found'
                    valid = False
                if not 'type' in data:
                    context['comments'] = 'Err:type not found'
                    valid = False
                else:
                    if data['type'] != 'template':
                        context['comments'] = 'Err:type not match:%s'%data['type']
                        valid = False

                if not 'category' in data:
                    context['comments'] = 'Err:category not found'
                    valid = False
                f.close()

            if valid:
                tmpl = Template(sender=user,path=path,tid=data['tid'],
                            tname=data['tname'],category=data['category'])
                tmpl.save()


    context['username'] = user

    info = []
    info.append(['lw','1','abc'])
    info.append(['lw1','2','cde'])
    context['info'] = info

    return render(request, "tmpl.html", context)

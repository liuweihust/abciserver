from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
from django.http import HttpResponseRedirect
from user.models import DataTemplate
import json

BASE_DIR="./static/"

def template(request):
    #return HttpResponse("hello")
    cat = request.path.split('/')
    logging.debug("buyer path=%s" % (request.path))

    user = request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user

    #Handle new template req
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

            #FIXME: send templates to blockchain here

            if valid:
                tmpl = DataTemplate(sender=user,path=path,tid=data['tid'],
                            tname=data['tname'],category=data['category'])
                tmpl.save()

    #Prepare template list
    info = []
    tmpls = DataTemplate.objects.all().filter(sender=user)
    for item in tmpls:
        #info.append([item.tname,item.category,item.sender,item.path])
        info.append([item.tid, item.path, item.time,item.tname, item.category])
    context['info'] = info

    return render(request, "tmpl.html", context)

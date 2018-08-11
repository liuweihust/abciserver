from django.http import HttpResponse
from django.shortcuts import render,render_to_response
import logging
import os
import json
from django.http import HttpResponseRedirect
from user import utils
import base64
BASE_DIR="./static/"

def query(request):
    user =  request.session.get('username', None)
    if user is None:
        return HttpResponseRedirect('/login.html')

    context = {}
    context['username'] = user

    if 'querytype' in request.GET:
        id = ''
        if 'keyword' in request.GET:
            id = request.GET['keyword']

        qa = []
        rawarray,decodearray = utils.query(request.GET['querytype'],id)

        for i in range(len(rawarray)):
            if len(id) == 0:
                name = rawarray[i]['hash']
            else:
                name = id

            dpath = os.path.join(BASE_DIR,'decode'+name+'.json')
            with open( dpath, 'w') as f:
                f.write(json.dumps(decodearray[i]))
                f.close()

            qpath = os.path.join(BASE_DIR, 'query' + name + '.json')
            with open(qpath, 'w') as f:
                f.write(json.dumps(rawarray[i]))
                f.close()

            qa.append([name,qpath,dpath])
        context['result'] = qa

    return render(request, "query.html", context)


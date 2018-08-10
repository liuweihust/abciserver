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
        res = utils.query(request.GET['querytype'],id)
        for item in res:
            qdict = {}
            for td in item['tx_result']['tags']:
                key = base64.b64decode(td['key']).decode('utf-8')
                value = base64.b64decode(td['value']).decode('utf-8')
                qdict[str(key)] = value

            if len(id) != 0:
                if request.GET['querytype'] == 'template':
                    if id != qdict['tid']:
                        continue
                elif request.GET['querytype'] == 'data':
                    if id != qdict['did']:
                        continue
                elif request.GET['querytype'] == 'contract':
                    if id != qdict['cid']:
                        continue
                elif request.GET['querytype'] == 'transaction':
                    if id != qdict['sid']:
                        continue
                else:
                    continue


            if len(id) == 0:
                name = item['hash']
            else:
                name = id

            qdict['tx'] = json.loads(base64.b64decode(item['tx']).decode('utf-8'))
            dpath = os.path.join(BASE_DIR,'decode'+name+'.json')
            with open( dpath, 'w') as f:
                f.write(json.dumps(qdict))
                f.close()

            qpath = os.path.join(BASE_DIR, 'query' + name + '.json')
            with open(qpath, 'w') as f:
                f.write(json.dumps(item))
                f.close()

            qa.append([name,qpath,dpath])
        context['result'] = qa

    return render(request, "query.html", context)


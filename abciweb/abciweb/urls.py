"""abciweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.static import serve
import logging

from django.conf.urls import url
from abciweb import settings
from user import view,login,templates,data,trans,query,offer

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^login.html$', login.loginform),
    url(r'^authpost$', login.auth),
    url(r'^user.html$', view.user),
    url(r'^tmpl.html$', templates.template),
    url(r'^data.html$', data.data),
    url(r'^offer.html$', offer.offer),
    url(r'^trans.html$', trans.trans),
    url(r'^query.html$', query.query),
]

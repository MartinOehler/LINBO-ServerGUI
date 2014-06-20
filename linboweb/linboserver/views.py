# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

from django.template import loader, Context
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt    
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib import messages

import os
import string
import errno
from django.core.files import File

from linboweb.linboserver.models import client as linboclient
from linboweb.linboserver.models import partitionSelection
from linboweb.linboserver.models import partition
from linboweb.linboserver.models import vm
from linboweb.linboserver.models import clientGroup

LINBO_USERNAME = getattr(settings, 'LINBO_USERNAME', 'linbouser')

editorlist = [ 'Edit Partition Selections',
               'Edit Operating Systems',
               'Edit Virtual Machines',
               'Edit PXE-Boot Configurations',
               'Edit Client Configurations',
               'Edit Client Groups' ]



# https://djangosnippets.org/snippets/1703/
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)


@csrf_exempt
@never_cache
def login_password(request,
                   template='login.html'):

    username = password = ''
    state = 'Please log in'
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # add username to session
                request.session["LINBO_USERNAME"] = username;   

                return HttpResponseRedirect(reverse('linboserver_main'));           
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect. Try again."

    return render_to_response('login.html',{'state':state, 'username': username},
                              context_instance=RequestContext(request))

@never_cache
@login_required
def leave(request):
    logout(request)
    return HttpResponseRedirect(reverse('linboserver_login'))
#    return HttpResponseRedirect("https://192.168.101.147/linboweb/")
#    return render_to_response('login.html',{'state':'', 'username': ''},
#                              context_instance=RequestContext(request))


@csrf_exempt
@never_cache
@login_required
def main(request,
         template='main.html'):

    clientgroups=clientGroup.objects.all()

    return render_to_response('main.html',
                              {'clientgroups': clientgroups},
                              context_instance=RequestContext(request))

@csrf_exempt
@never_cache
@login_required
def imageadmin(request,
               template='imageadmin.html'):

    return render_to_response('imageadmin.html', 
                              {},
                              context_instance=RequestContext(request))
                     
@csrf_exempt
@never_cache
@login_required
def config(request,
         template='config.html'):

    return render_to_response('config.html', 
                              {'editorlist':editorlist},
                              context_instance=RequestContext(request))
 

@csrf_exempt
@never_cache
@login_required
def wizard(request,
           template='wizard.html'):

    clientgroups=clientGroup.objects.all()
    templates=linboclient.objects.filter(template=True)

    return render_to_response('wizard.html', 
                              {'clientgroups':clientgroups,
                               'templates':templates},
                              context_instance=RequestContext(request))

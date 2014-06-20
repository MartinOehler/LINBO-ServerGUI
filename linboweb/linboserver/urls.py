# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

from django.conf.urls.defaults import *
from linboweb.linboserver.views import login_password
from linboweb.linboserver.views import leave
from linboweb.linboserver.views import main
from linboweb.linboserver.views import wizard
from linboweb.linboserver.views import config
from linboweb.linboserver.views import imageadmin
from linboweb.linboserver.views import group_required



urlpatterns = patterns('',
    url(r'^$',             login_password,   name='linboserver_login'),
    url(r'^logout/$',      leave,  	     name='linboserver_logout'),
    url(r'^main/$',        main,  	     name='linboserver_main'),
    url(r'^wizard/$',      wizard,  	     name='linboserver_wizard'),
    url(r'^imageadmin/$',  imageadmin, 	     name='linboserver_imageadmin'),
    url(r'^config/$',      group_required('linboadmin')(config),  name='linboserver_config')
)

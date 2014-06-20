# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

import os,pwd
import sys

sys.path.append('/srv/django/linboweb/')
sys.path.append('/srv/django/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'linboweb.settings'
os.environ["HOME"] = pwd.getpwuid(os.getuid()).pw_dir

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

# https support according to modwsgi dcumentation
def application(environ, start_response):
    if environ['wsgi.url_scheme'] == 'https':
        environ['HTTPS'] = 'on'
    return _application(environ, start_response)


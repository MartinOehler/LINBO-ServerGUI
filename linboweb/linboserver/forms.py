# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

from django.forms import ModelForm
from django.forms import Form
from django.forms import ModelChoiceField

from django.forms.widgets import RadioSelect
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.widgets import TextInput
from django.forms.widgets import Textarea
from django.forms.widgets import DateInput
from django.contrib.admin import widgets

from linboweb.linboserver.models import partition
from linboweb.linboserver.models import partitionSelection
from linboweb.linboserver.models import os
from linboweb.linboserver.models import vm
from linboweb.linboserver.models import client
from linboweb.linboserver.models import clientGroup
from linboweb.linboserver.models import pxelinuxcfg


class partitionForm(ModelForm):
    class Meta:
        model = partition

class partitionSelectionForm(ModelForm):
    class Meta:
        model = partitionSelection

class osForm(ModelForm):
    partitionselection = ModelChoiceField(queryset=partitionSelection.objects.all())
    class Meta:
        model = os
        
class vmForm(ModelForm):
    class Meta:
        model = vm

class clientForm(ModelForm):
    pxelinuxconfiguration = ModelChoiceField(queryset=pxelinuxcfg.objects.all())
    class Meta:
        model = client

class clientGroupForm(ModelForm):
    class Meta:
        model = clientGroup

class pxelinuxcfgForm(ModelForm):
    class Meta:
        model = pxelinuxcfg
        widgets = {
            'configuration': Textarea(attrs={'cols': 80, 'rows': 40}),
        }

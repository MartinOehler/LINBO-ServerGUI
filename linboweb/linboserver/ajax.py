# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

from dajax.core import Dajax
from dajaxice.core import dajaxice_functions
from dajaxice.utils import deserialize_form

from django.template.loader import render_to_string

# decorators
from dajaxice.decorators import dajaxice_register
from django.contrib.auth.decorators import login_required

# to use dajax, we need to render the views in a request context
from django.template import RequestContext

from linboweb.linboserver.models import partition
from linboweb.linboserver.models import disk
from linboweb.linboserver.models import partitionSelection
from linboweb.linboserver.models import os as operatingsystem
from linboweb.linboserver.models import vm
from linboweb.linboserver.models import pxelinuxcfg
from linboweb.linboserver.models import client 
from linboweb.linboserver.models import clientGroup

from linboweb.linboserver.forms import partitionForm
from linboweb.linboserver.forms import partitionSelectionForm
from linboweb.linboserver.forms import osForm
from linboweb.linboserver.forms import vmForm
from linboweb.linboserver.forms import clientForm
from linboweb.linboserver.forms import clientGroupForm
from linboweb.linboserver.forms import pxelinuxcfgForm

from django.forms.widgets import Select
from django.forms import CharField

# TODO: correct csrf handling
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from datetime import date
from datetime import datetime

from django.utils import simplejson
from copy import deepcopy

import binascii
import socket
import struct
import os
import subprocess
import shlex
import re
from subprocess import call
from array import *

def ipToInteger(ip):
    ip = unicode(ip)
    try:
        return struct.unpack('!I', socket.inet_pton(socket.AF_INET, ip))[0]
    except socket.error:
        try:
            hi, lo = struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, ip))
            return (hi << 64) | lo
        except socket.error:
            return 0


@csrf_exempt
@login_required
@dajaxice_register
def displayeditor(request,
                  option):
  
    dajax = Dajax()
    render=''

    if option == 'Edit Partition Selections':
        partitionSelections=partitionSelection.objects.all()

        render = render_to_string('editor_div.html', 
                                  { 'partitionSelections':partitionSelections,
                                    'partitionSelectionAdminVisible':'1'})


    if option == 'Edit Virtual Machines':
        vms=vm.objects.all()

        render = render_to_string('editor_div.html', 
                                  { 'vms':vms,
                                    'vmAdminVisible':'1'})


    if option == 'Edit Operating Systems':
        oss=operatingsystem.objects.all()
            

        render = render_to_string('editor_div.html', 
                                  { 'oss':oss,
                                    'osAdminVisible':'1'})


    if option == 'Edit PXE-Boot Configurations':
        pxelinuxcfgs=pxelinuxcfg.objects.all()

        render = render_to_string('editor_div.html', 
                                  { 'pxelinuxcfgs':pxelinuxcfgs,
                                    'pxelinuxcfgAdminVisible':'1'})


    if option == 'Edit Client Configurations':
        clients=client.objects.all()

        render = render_to_string('editor_div.html', 
                                  { 'clients':clients,
                                    'clientAdminVisible':'1'})

    if option == 'Edit Client Groups':
        clientGroups=clientGroup.objects.all()

        render = render_to_string('editor_div.html', 
                                  { 'clientGroups':clientGroups,
                                    'clientGroupAdminVisible':'1'})


    #print render
#    js = '$("#editor").html("%s")' % render
 #   print js
  #  dajax.script(js)
    dajax.assign('#editor','innerHTML',str(render))
#    dajax.alert("$('#editor').html(\'"+render+"\');")
#    dajax.script("document.getElementById('#editor').innerHTML = \'"+render+"\';")
    
   # dajax.script('reload();')
    return dajax.json()



###############################################################################
#                         Create output files
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def exportClientConfiguration(request,
                              option):

    dajax = Dajax()
    dajax.alert("export client configuration entered")

    # get all client groups
    for clientgroup in clientGroup.objects.all():
        for myclient in clientgroup.members.all():
            
            # update client order
            myclient.ipaddrint = ipToInteger(myclient.ipaddr)
            myclient.save()

            # open the file
            filename="/srv/linbo/cache/start.conf-" + myclient.ipaddr
            f=open(filename,'w')

            # write header of general LINBO section
            f.write("[LINBO]\n")
            f.write("Cache = " + myclient.cache + "\n")
            f.write("Server = " + myclient.server + "\n")
            # Removed 2014-03-24, moved to pxelinux.cfg by request of KK
            # f.write("Smbdir = " + myclient.smbdir + "\n")
            f.write("AutoStartTimeout = " + str(myclient.autostarttimeout) + "\n")
            f.write("AutoStartOS = " + str(myclient.autostartos) + "\n")
            f.write("AutoPartition = " + str(myclient.autopartition).replace('True','yes').replace('False','no') + "\n")
            f.write("AutoSync = " + str(myclient.autosync).replace('True','yes').replace('False','no') + "\n")
            f.write("InstallMBR  = " + str(myclient.installmbr).replace('True','yes').replace('False','no') + "\n")
            f.write("TorrentEnabled = " + str(myclient.torrentenabled).replace('True','yes').replace('False','no') + "\n")
            if myclient.torrentenabled == True:
                f.write("DownloadType = torrent\n\n")
            else:
                f.write("DownloadType = rsync\n\n")

            ipinhex=binascii.hexlify(socket.inet_aton(myclient.ipaddr)).upper()
            filenamebootconf="/tftpboot/pxelinux.cfg/" + ipinhex
            pxe=open(filenamebootconf,'w')
            pxe.write(myclient.pxelinuxconfiguration.configuration)
            pxe.close()

            # get disk that holds the cache
            cachedisk=myclient.cache.strip('0123456789')
            cachediskwritten=False

            for osentry in myclient.osentries.all():
                pselection=osentry.partitionselection
                # collect necessary hard disks
                for disk in pselection.disks.all():
                    if disk.device==cachedisk:
                        cachediskwritten=True

                    f.write("[Disk]\n")
                    f.write("Dev = " + str(disk.device) + "\n")
                    f.write("Type = " + str(disk.partitiontable) + "\n\n")
                        
                for part in pselection.partitions.all():
                    f.write("[Partition]\n")
                    f.write("Osid = " + str(osentry.osid) + "\n")
                    f.write("Dev = " + part.device + "\n")
                    f.write("Size = " + str(part.size) + "\n")
                    f.write("FSType = " + str(part.fstype) + "\n")
                    f.write("Image = " + str(part.image) + "\n")
                    f.write("Bootable = " + str(part.bootable).replace('True','yes').replace('False','no') + "\n")
                    if part.quicksync != None:
                        f.write("Quicksync = " + part.quicksync + "\n\n")

                f.write("[OS]\n")
                f.write("Osid = " + str(osentry.osid) + "\n")
                f.write("Name = " + osentry.name + "\n")
                f.write("Description = " + osentry.description + "\n")
                f.write("Method = " + osentry.bootmethod + "\n")
                f.write("Boot = " + osentry.boot + "\n")
                f.write("Root = " + osentry.root + "\n")
                f.write("Kernel = " + osentry.kernel + "\n")
                f.write("Initrd = " + osentry.initrd + "\n")
                f.write("Append = " + osentry.append + "\n")
                f.write("Patches = " + osentry.patches + "\n\n")

            if cachediskwritten==False:
                f.write("[Disk]\n")
                f.write("Dev = " + str(cachedisk) + "\n")
                f.write("Type = msdos\n\n")

            # write cache partitions
            f.write("# Cache Partition\n")
            f.write("[Partition]\n")
            f.write("Dev = " + myclient.cache + "\n")
            f.write("Size = -1\n")
            f.write("FSType = reiserfs\n\n")


            for virtualMachine in myclient.vms.all():
                f.write("[VM]\n")
                f.write("Name = " + virtualMachine.name + "\n")
                f.write("Patches = " + virtualMachine.patches + "\n")


            f.close()
    
    dajax.alert("Configuration written to disk.")

    return dajax.json()


###############################################################################
#                 Manage Partition Selections (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def partitionSelectionChanged(request,
                              selection):

    dajax = Dajax()
    render=''

    
    if selection == 'New':
        print "New entered"
#        newPartitionSelectionFormset=modelformset_factory(partitionSelection,
#                                                          form=partitionSelectionForm)

        form=partitionSelectionForm()


        render = render_to_string('partitionselection_div.html', 
                                  { 'form':form,
                                    'partitionSelectionDescrVisible':'1',
                                    'partitionSelectionDivVisible':'1'})
        
    if selection != 'New' and selection != '':

        selectedPartition = partitionSelection.objects.get(name=selection)

        # form=partitionSelectionForm(instance=selectedPartition)
        form=''

        partitionFormset=modelformset_factory(partition,
                                              form=partitionForm,
                                              extra=4)

        partitions=partitionFormset(queryset=selectedPartition.partitions.all())

        render = render_to_string('partitionselection_div.html', 
                                  { 'partitions':partitions,
                                    'partitionSelectionDescrVisible':'',
                                    'partitionSelectionDivVisible':'1'})

    dajax.assign('#partitionselectiondiv','innerHTML',render)
    # dajax.script('reload();')
    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def remove_partitionselection(request,
                              selectedpartitionselection):

    dajax = Dajax()
    pselection=''
    success=''

    print "remove_partitionselection entered"
    if request.POST:
        try:
            pselection=partitionSelection.objects.get(name=selectedpartitionselection)
            print "Partition Selection found"
        except partitionSelection.DoesNotExist:
            pselection=None
            print "Partition selection does not exist"
            
        if pselection != None:
            # get partition
            try:
                try:
                    for mypartition in pselection.partitions.all():
                        print "Removing Partition %s" % mypartition.name
                        pselection.partitions.remove(mypartition)
                        mypartition.delete()

                    for disk in pselection.disks.all():
                        print "Removing Disk %s" % disk.device
                        pselection.disks.remove(disk)
                        disk.delete()
                except: 
                    print "no partitions"
                    success=None
                finally:
                    pselection.delete()
            except:
                print "An error during removal of partitions occured." 
                success=None
          
        if success==None:
            dajax.alert("Delete partition selection: failure.")
        else:
            dajax.alert("Delete partition selection: success.")  

    return dajax.json()
  

@csrf_exempt
@login_required
@dajaxice_register
def save_partitionselection(request,
                            option,
                            selector,
                            dataPartitionSelection,
                            dataPartitions):

    dajax = Dajax()
    success=''

    if request.POST:
        if option == 'Save':
            if selector=='New':
                # this is a single form
                print "Selector new entered"
                # TODO: distinguish between different form types
                # this value is ignored
                deserialized_form = deserialize_form(dataPartitionSelection)

                # this holds our data for the new partition selection
                deserialized_form2 = deserialize_form(dataPartitions)

                form = partitionSelectionForm(deserialized_form2)
                print "BEFORE VALIDITY CHECK!!! %s " % deserialized_form2.get("name")

#                if form.name.value != '' and form.description.value != '':
#                    try:
#                        newpartitionselection = partitionSelection()
#                        newpartitionselection.name = form.name.value
#                        newpartitionselection.description = form.description.value
#                        newpartitionselection.save()
                if form.is_valid():
                    print "form is valid!"
                    try:
                        form.save()                
                    except:
                        success=None
                        print "Creation of partitionselection failed."
                else:
                    success=None

            else:
                partitionFormset = modelformset_factory(partition,
                                                        form=partitionForm,
                                                        extra=4)

                deserialized_form_partitions = deserialize_form(dataPartitions)

                print "DESERIALIZED FORM"
                print deserialized_form_partitions
                formset_partitions = partitionFormset(deserialized_form_partitions)
                print "BEFORE VALIDITY CHECK!!!"
           
                if formset_partitions.is_valid():
                    
                    try:
                        partitions=formset_partitions.save()
                        # TODO: add to partitionSelection
                        selectedPartition = partitionSelection.objects.get(name=selector)

                        partitionset=set()
                        
                        for new_partitions in partitions:
                            selectedPartition.partitions.add(new_partitions)
                            partitionnameforset=new_partitions.device.strip('0123456789')
                            print partitionnameforset
                            partitionset.add(partitionnameforset)
                        
                        # clean up old disks
                        for olddisk in selectedPartition.disks.all():
                            partitionset.add(olddisk.device.strip('0123456789'))
                            print "Removing Disk %s" % olddisk.device
                            selectedPartition.disks.remove(olddisk)
                            olddisk.delete()

                        # add new disks
                        for setitem in partitionset:
                            newdisk=disk(device=str(setitem),
                                         partitiontable="msdos")
                            newdisk.id=None
                            newdisk.save()
                            selectedPartition.disks.add(newdisk)
                            selectedPartition.save()
                    except:
                        success=None     
                
                else:
                    Success=None

        if success==None:
            dajax.alert("Save partition selection: failure.")
        else:
            dajax.alert("Save partition selection: success.")


    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def remove_partition(request,
                     selectedpartitionselection,
                     selectedpartition):

    dajax = Dajax()
    pselection=''
    success=''
    print "remove_partition entered"

    if request.POST:
        try:
            pselection=partitionSelection.objects.get(name=selectedpartitionselection)
            print "Partition Selection found"
        except partitionSelection.DoesNotExist:
            success=None
            pselection=None
            print "Partition selection does not exist"
            
        
        if pselection != None:
            # get partition
            try:
                mypartition=pselection.partitions.get(name=selectedpartition)
                print "Partition found %s" % mypartition.name
                pselection.partitions.remove(mypartition)
                mypartition.delete()
                pselection.save()

                # disk cleanup logic
                # clean up old disks
                for olddisk in pselection.disks.all():
                    pselection.disks.remove(olddisk)
                    olddisk.delete()

                partitionset=set()

                for part in pselection.partitions.all():
                    partitionnameforset=part.device.strip('0123456789')
                    print partitionnameforset
                    partitionset.add(partitionnameforset)

                # add new disks
                for setitem in partitionset:
                    newdisk=disk(device=str(setitem),
                                 partitiontable="msdos")
                    newdisk.id=None
                    newdisk.save()
                    pselection.disks.add(newdisk)
                    pselection.save()

            except partition.DoesNotExist:
                print "Partition does not exist"
                success=None

        if success==None:
            dajax.alert("Delete partition: failure.")
        else:
            dajax.alert("Save partition: success.")
            
    return dajax.json()

###############################################################################
#                 Manage Partition Selections (end)
###############################################################################


###############################################################################
#                 Manage VMs (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def vmSelectionChanged(request,
                       selection):

    dajax = Dajax()
    render=''
    
    if selection == 'New':
        form=vmForm()

        render = render_to_string('vm_div.html', 
                                  { 'form':form,
                                    'vmDescrVisible':'1',
                                    'vmDivVisible':'1',
                                    'vmShowDelete':''})
        
    if selection != 'New' and selection != '':
        selectedVM = vm.objects.get(name=selection)

        form=vmForm(instance=selectedVM)

        render = render_to_string('vm_div.html', 
                                  { 'form':form,
                                    'vmDescrVisible':'1',
                                    'vmDivVisible':'1',
                                    'vmShowDelete':'1'})

    dajax.assign('#vmdiv','innerHTML',render)
    return dajax.json()


@csrf_exempt
@login_required
@dajaxice_register
def remove_vm(request,
              selectedvm):

    dajax = Dajax()
    vmselection=''
    success=''

    if request.POST:
        try:
            vmselection=vm.objects.get(name=selectedvm)
        except vm.DoesNotExist:
            vmselection=None
            
        if vmselection != None:
            try:
                vmselection.delete()
            except:
                success=None
            

        if success==None:
            dajax.alert("Delete VM: failure.")
        else:
            dajax.alert("Delete VM: success.")

    return dajax.json()
  

@csrf_exempt
@login_required
@dajaxice_register
def save_vm(request,
            option,
            selector,
            datavm):

    dajax = Dajax()
    success=''

    if request.POST:
        if option == 'Save':
            deserialized_form = deserialize_form(datavm)

            vmname=deserialized_form.get("name")

            # check whether the vm already exists
            vmsearch=''
            try:
                vmsearch=vm.objects.get(name=vmname)
            except vm.DoesNotExist:
                vmsearch=None

            # TODO: do we want this? perhaps make name read-only field

            # this is a new entry
            if vmsearch==None:
                form = vmForm(deserialized_form)

                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            # this is an already existing object, update values
            else:
                form = vmForm(instance=vmsearch, data=deserialized_form)
                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            if success==None:
                dajax.alert("Save VM: failure.")
            else:
                dajax.alert("Save VM: success.")


    return dajax.json()


###############################################################################
#                 Manage VMs (end)
###############################################################################


###############################################################################
#                 Manage Client Groups (start)
###############################################################################

@login_required
@dajaxice_register
def clientGroupSelectionChanged(request,
                                selection):

    dajax = Dajax()
    render=''

    
    if selection == 'New':
        print "New entered"

        form=clientGroupForm()

        render = render_to_string('clientgroup_div.html', 
                                  { 'form':form,
                                    'clientGroupDescrVisible':'1',
                                    'clientGroupDivVisible':'1',
                                    'clientGroupShowDelete':''})
        
    if selection != 'New' and selection != '':

        selectedClientGroup = clientGroup.objects.get(name=selection)

        form=clientGroupForm(instance=selectedClientGroup)

        render = render_to_string('clientgroup_div.html', 
                                  { 'form':form,
                                    'clientGroupDescrVisible':'1',
                                    'clientGroupDivVisible':'1',
                                    'clientGroupShowDelete':'1'})

    dajax.assign('#clientGroupdiv','innerHTML',render)
    # dajax.script('reload();')
    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def remove_clientGroup(request,
                       selectedclientGroup):

    dajax = Dajax()
    cgselection=''
    success=''

    if request.POST:
        try:
            cgselection=clientGroup.objects.get(name=selectedclientGroup)
            print "Client Group found"
        except clientGroup.DoesNotExist:
            cgselection=None
            print "Client Group does not exist"
            
        if cgselection != None:
            # get client
            try:
                try:
                    for myclient in cgselection.clients.all():
                        print "Removing client %s" % myclient.name
                        cgselection.clients.remove(myclient)
                        # we do NOT remove the client!
                        # although the client will not be generated
                        # myclient.delete()
                except:
                    print "no clients"
                finally:
                    cgselection.delete()
            except:
                success=None
                
            if success==None:
                dajax.alert("Delete client group: failure.")
            else:
                dajax.alert("Delete client group: success.")

            
    return dajax.json()
  
@csrf_exempt
@login_required
@dajaxice_register
def save_clientGroup(request,
                     option,
                     selector,
                     dataClientGroup):

    dajax = Dajax()
    success=''

    if request.POST:
        if option == 'Save':
            deserialized_form = deserialize_form(dataClientGroup)
            print "deserialized form %s" % deserialized_form

            cgname=deserialized_form.get("name")

            cgsearch=''
            try:
                cgsearch=clientGroup.objects.get(name=cgname)
            except clientGroup.DoesNotExist:
                cgsearch=None

            # TODO: do we want this? perhaps make name read-only field

            # this is a new entry
            if cgsearch==None:
                form = clientGroupForm(deserialized_form)

                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None
                
            else:
                form = clientGroupForm(instance=cgsearch, data=deserialized_form)
                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            if success==None:
                dajax.alert("Save client group: failure.")
            else:
                dajax.alert("Create client group: success.")


    return dajax.json()


###############################################################################
#                 Manage Client Groups (end)
###############################################################################


###############################################################################
#                 Manage OSs (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def osSelectionChanged(request,
                       selection):

    dajax = Dajax()
    render=''
    
    if selection == 'New':
        form=osForm()

        render = render_to_string('os_div.html', 
                                  { 'form':form,
                                    'osDescrVisible':'1',
                                    'osDivVisible':'1',
                                    'osShowDelete':''})
        
    if selection != 'New' and selection != '':
        print "selection===== %s" % selection
        selectedOS = operatingsystem.objects.get(name=selection)

        form=osForm(instance=selectedOS)

        render = render_to_string('os_div.html', 
                                  { 'form':form,
                                    'osDescrVisible':'1',
                                    'osDivVisible':'1',
                                    'osShowDelete':'1'})

    dajax.assign('#osdiv','innerHTML',render)
    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def remove_os(request,
              selectedos):

    dajax = Dajax()
    osselection=''
    success=''

    if request.POST:
        try:
            osselection=operatingsystem.objects.get(name=selectedos)
        except os.DoesNotExist:
            osselection=None
            
        if osselection != None:
            try:
                osselection.delete()
            except:
                success=None
            
        if success==None:
            dajax.alert("Delete OS: failure.")
        else:
            dajax.alert("Delete OS: success.")

    return dajax.json()
  
@csrf_exempt
@login_required
@dajaxice_register
def save_os(request,
            option,
            selector,
            dataos):

    dajax = Dajax()
    success =''

    if request.POST:
        if option == 'Save':
            deserialized_form = deserialize_form(dataos)
            print deserialized_form

            osname=deserialized_form.get("name")

            # check whether the os already exists
            ossearch=''
            try:
                ossearch=operatingsystem.objects.get(name=osname)
            except operatingsystem.DoesNotExist:
                ossearch=None

            # TODO: do we want this? perhaps make name read-only field

            # this is a new entry
            if ossearch==None:
                form = osForm(deserialized_form)

                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            # this is an already existing object, update values
            else:
                form = osForm(instance=ossearch, data=deserialized_form)
                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None                 

            if success==None:
                dajax.alert("Save OS: failure.")
            else:
                dajax.alert("Save OS: success.")


    return dajax.json()


###############################################################################
#                 Manage OSs (end)
###############################################################################

###############################################################################
#                 Manage PXELINUXCFGs (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def pxelinuxcfgSelectionChanged(request,
                                selection):

    dajax = Dajax()
    render=''
    
    if selection == 'New':
        form=pxelinuxcfgForm()

        render = render_to_string('pxelinuxcfg_div.html', 
                                  { 'form':form,
                                    'pxelinuxcfgDescrVisible':'1',
                                    'pxelinuxcfgDivVisible':'1',
                                    'pxelinuxcfgShowDelete':''})
        
    if selection != 'New' and selection != '':
        selectedPXELINUXCFG = pxelinuxcfg.objects.get(name=selection)

        form=pxelinuxcfgForm(instance=selectedPXELINUXCFG)

        render = render_to_string('pxelinuxcfg_div.html', 
                                  { 'form':form,
                                    'pxelinuxcfgDescrVisible':'1',
                                    'pxelinuxcfgDivVisible':'1',
                                    'pxelinuxcfgShowDelete':'1'})

    dajax.assign('#pxelinuxcfgdiv','innerHTML',render)
    return dajax.json()


@csrf_exempt
@login_required
@dajaxice_register
def remove_pxelinuxcfg(request,
              selectedpxelinuxcfg):

    dajax=Dajax()
    pxelinuxcfgselection=''
    success=''

    if request.POST:
        try:
            pxelinuxcfgselection=pxelinuxcfg.objects.get(name=selectedpxelinuxcfg)
        except pxelinuxcfg.DoesNotExist:
            pxelinuxcfgselection=None
            success=None
            
        if pxelinuxcfgselection != None:
            try:
                pxelinuxcfgselection.delete()
            except:
                success=None

        if success==None:
            dajax.alert("Delete pxelinuxcfg: failure.")
        else:
            dajax.alert("Delete pxelinuxcfg: success.")
            
    return dajax.json()
  
@csrf_exempt
@login_required
@dajaxice_register
def save_pxelinuxcfg(request,
                     option,
                     selector,
                     datapxelinuxcfg):

    dajax = Dajax()
    success=''

    if request.POST:
        if option == 'Save':
            deserialized_form = deserialize_form(datapxelinuxcfg)

            pxelinuxcfgname=deserialized_form.get("name")

            # check whether the pxelinuxcfg already exists
            pxelinuxcfgsearch=''
            try:
                pxelinuxcfgsearch=pxelinuxcfg.objects.get(name=pxelinuxcfgname)
            except pxelinuxcfg.DoesNotExist:
                pxelinuxcfgsearch=None

            # TODO: do we want this? perhaps make name read-only field

            # this is a new entry
            if pxelinuxcfgsearch==None:
                form = pxelinuxcfgForm(deserialized_form)

                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                        dajax.alert("Creation of pxelinuxcfg failed.")
                else:
                    dajax.alert("Invalid data entered. Are all fields correctly filled?")

            # this is an already existing object, update values
            else:
                form = pxelinuxcfgForm(instance=pxelinuxcfgsearch, data=deserialized_form)
                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None                 

            if success==None:
                dajax.alert("Save pxelinuxcfg: failure.")
            else:
                 dajax.alert("Save pxelinuxcfg: success.")

    return dajax.json()


###############################################################################
#                 Manage PXELINUXCFGs (end)
###############################################################################


###############################################################################
#                 Manage Clients (start)
###############################################################################

@login_required
@dajaxice_register
def clientSelectionChanged(request,
                           selection):

    dajax = Dajax()
    render=''
    
    if selection == 'New':
        form=clientForm()

        render = render_to_string('client_div.html', 
                                  { 'form':form,
                                    'clientDescrVisible':'1',
                                    'clientDivVisible':'1',
                                    'clientShowDelete':''})
        
    if selection != 'New' and selection != '':
        selectedClient = client.objects.get(ipaddr=selection)

        form=clientForm(instance=selectedClient)

        render = render_to_string('client_div.html', 
                                  { 'form':form,
                                    'clientDescrVisible':'1',
                                    'clientDivVisible':'1',
                                    'clientShowDelete':'1'})

    dajax.assign('#clientdiv','innerHTML',render)
    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def remove_client(request,
              selectedclient):

    dajax = Dajax()
    clientselection=''
    success=''

    if request.POST:
        try:
            clientselection=client.objects.get(ipaddr=selectedclient)
        except client.DoesNotExist:
            clientselection=None

            
        if clientselection != None:
            try:
                clientselection.delete()
            except:
                success=None

        if success==None:
            dajax.alert("Delete Client: failure.")
        else:
            dajax.alert("Delete Client: success.")

            
    return dajax.json()
  

@csrf_exempt
@login_required
@dajaxice_register
def save_client(request,
                     option,
                     selector,
                     dataclient):

    dajax = Dajax()
    success=''

    if request.POST:
        if option == 'Save':
            deserialized_form = deserialize_form(dataclient)

            clientip=deserialized_form.get("ipaddr")

            # check whether the client already exists
            clientsearch=''
            try:
                clientsearch=client.objects.get(ipaddr=clientip)
            except client.DoesNotExist:
                clientsearch=None

            # TODO: do we want this? perhaps make name read-only field

            # this is a new entry
            if clientsearch==None:
                form = clientForm(deserialized_form)

                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            # this is an already existing object, update values
            else:
                form = clientForm(instance=clientsearch, data=deserialized_form)
                if form.is_valid():
                    try:
                        form.save()                
                    except:
                        success=None
                else:
                    success=None

            if success==None:
                dajax.alert("Save client: failure.")
            else:
                dajax.alert("Save client: success.")

    return dajax.json()


###############################################################################
#                 Manage Clients (end)
###############################################################################

###############################################################################
#                 Wizard (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def createClientFromTemplate(request,
                             clientgroupselection,
                             clienttemplateselection,
                             ipaddr):

    dajax = Dajax()
    print "createclientfromtemplate entered"

    if request.POST:
        if clientgroupselection!='' and clienttemplateselection!='' and ipaddr!='':

            clientgroup=clientGroup.objects.get(name=clientgroupselection)
            clienttemplate=client.objects.get(description=clienttemplateselection,template=1)

            try:
                ipcheck=client.objects.filter(ipaddr=ipaddr)
            except client.DoesNotExist:
                ipcheck=1

            if ipcheck.count() > 0:
                dajax.alert("The IP already exists.")
            else:
                newobj=deepcopy(clienttemplate)

                # set id to none which effectively makes django assign a
                # new id when saving the object
                newobj.pk=None
                # TODO
                # newobj.date=
                # this is not a template
                newobj.template=False
                newobj.ipaddr=ipaddr
                newobj.description=''
                newobj.save()
                new_osentries=clienttemplate.osentries.all()
                newobj.osentries = new_osentries

                new_vms=clienttemplate.vms.all()
                newobj.vms = new_vms

                newobj.save()
                
                # add to client group
                clientgroup.members.add(newobj)
                clientgroup.save()
                dajax.alert("Client successfully created.")
        else:
            dajax.alert("Some values are missing, cannot create object.")
        
    return dajax.json()
        
###############################################################################
#                 Wizard (end)
###############################################################################

###############################################################################
#                 Imageadmin (start)
###############################################################################

@csrf_exempt
@login_required
@dajaxice_register
def loadImageAdminDiv(request):

    dajax = Dajax()
    print "createimageadmin entered"

    # find files in /srv/linbo/incoming
    filesincoming = os.listdir('/srv/linbo/incoming/')
    filescache    = os.listdir('/srv/linbo/cache/')

    filescache.sort()
    filesincoming.sort()

    imageadmin=''
    imageadmin+='<div class="row">'
    imageadmin+='<div class="large-4 columns">'
    imageadmin+='<p>Incoming Directory:</p>'
    imageadmin+='<select id="fileselectorincoming" name="fileselectorincoming" size="7">'
    for filename in filesincoming:
        imageadmin += '<option>'+filename+'</option>'
    imageadmin+='</select>'
    imageadmin+='</div>'

    imageadmin+='<div class="large-3 columns text-center">'
    imageadmin+='<div class="row">'
    imageadmin+='<button type="button" class="button radius small" onclick="checkMoveOperation();">&raquo;</button>'
    imageadmin+='</div>'
    imageadmin+='<div class="row">'
    imageadmin+='<p>New filename (optional)</p>'
    imageadmin+='</div>'
    imageadmin+='<div class="row">'
    imageadmin+='<input id="newfilename" type="text" for="left-label">'
    imageadmin+='</div>'
    imageadmin+='</div>'

    imageadmin+='<div class="large-4 columns left">'
    imageadmin+='<p>Cache Directory:</p>'
    imageadmin+='<select id="fileselectorcache" size="7">'
    for filename in filescache:
        # exclude start.conf-
        if re.match(r"^start.conf-.*", filename):
            continue
        imageadmin += '<option disabled>'+filename+'</option>'
    imageadmin+='</select>'
    imageadmin+='</div>'
    imageadmin+='</div>'

    dajax.assign('#imageadmindiv','innerHTML',imageadmin)
    
    return dajax.json()

@csrf_exempt
@login_required
@dajaxice_register
def moveFileIncomingToCache(request,
                            filenameorig,
                            filenametarget):

    dajax = Dajax()
    print "moveFileIncomingToCache entered"  

    

    if filenameorig != filenametarget:
        try:
            arg2='/bin/cp -r /srv/linbo/incoming/'+filenameorig+' /srv/linbo/cache/'+filenametarget
            args2=shlex.split(arg2)
            retval2=subprocess.check_output(args2                                                                                 )
            print arg2 + " return value (not output) " + str(retval2)
        except subprocess.CalledProcessError,e:
            print "calledprocesserror in moveFileIncomingToCache"
            print e.cmd
            print e.returncode
            print e.output
            dajax.alert("Copy operation unsuccessful.")
        else:
            dajax.alert("Copy operation successful.")
    else:
        try:
            arg='/bin/cp -r /srv/linbo/incoming/'+filenameorig+' /srv/linbo/cache/'
            args=shlex.split(arg)
            retval=subprocess.check_output(args)
            print arg + " return value (not output) " + str(retval)
        except subprocess.CalledProcessError,e:
            print "calledprocesserror in moveFileIncomingToCache"
            print e.cmd
            print e.returncode
            print e.output
            dajax.alert("Copy operation unsuccessful.")
        else:
            dajax.alert("Copy operation successful.")
 

    dajax.script("window.location.reload();")
    
    return dajax.json()


###############################################################################
#                 Imageadmin (end)
###############################################################################

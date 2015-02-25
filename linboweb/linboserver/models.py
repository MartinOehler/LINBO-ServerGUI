# Author: Martin Oehler <oehler@knopper.net> 2013
# License: GPL V2

from django.db import models
from django.contrib import admin

from datetime import date
from datetime import datetime
from django.utils.dateformat import format

from ajax_select.fields import autoselect_fields_check_can_add
from django.contrib import admin


# osid is added during writing of the start.conf
class partition(models.Model):
    fstype_choices = (
        ('ext3', 'ext3'),
        ('ext4', 'ext4'),
        ('reiserfs','reiserfs'),
        ('ntfs', 'ntfs'),
        ('vfat', 'vfat'),
        ('swap', 'swap'),
        ('extended', 'extended'),
        )
    name     = models.CharField(max_length=80)
    device   = models.CharField(max_length=20)
    size     = models.BigIntegerField(default=0)
    fstype   = models.CharField(choices=fstype_choices,max_length=20,default="ext3",blank=False)
    image    = models.CharField(max_length=80,blank=True)
    bootable = models.BooleanField(default=False)
    quicksync = models.CharField(max_length=1024,blank=True)
    description = models.CharField(max_length=300,blank=True)

    def __unicode__(self):
        return self.device;

class disk(models.Model):
    partitiontable_choices = (
        ('msdos', 'msdos'),
        ('gpt','gpt'),
        )
    device         = models.CharField(max_length=20)
    partitiontable = models.CharField(choices=partitiontable_choices,max_length=20,default="msdos")

    def __unicode__(self):
        return self.device;

# better take a partition selection for the cache
class partitionSelection(models.Model):
    name        = models.CharField(max_length=80)
    disks       = models.ManyToManyField(disk,blank=True)
    partitions  = models.ManyToManyField(partition,blank=True)
    description = models.CharField(max_length=300,blank=True)

    def __unicode__(self):
        return self.name;

# OS Definition
# osid needed for efficient sync+start
# 2014-03-24: bootmethod kexec disabled
class os(models.Model):
    bootmethod_choices = (
        ('reboot','reboot'),
        ('local','local'),
        )
    osid               = models.CharField(max_length=10)
    name               = models.CharField(max_length=80)
    bootmethod         = models.CharField(choices=bootmethod_choices,max_length=10,default="reboot")
    boot               = models.CharField(max_length=80)
    root               = models.CharField(max_length=80)
    kernel             = models.CharField(max_length=80,blank=True)
    initrd             = models.CharField(max_length=80,blank=True)
    append             = models.CharField(max_length=200,blank=True)
    patches            = models.CharField(max_length=200,blank=True)
    partitionselection = models.ForeignKey(partitionSelection)
    description        = models.CharField(max_length=300,blank=True)

    def __unicode__(self):
        return self.name;


class vm(models.Model):
    name               = models.CharField(max_length=80)
    patches            = models.CharField(max_length=200,blank=True)
    description        = models.CharField(max_length=300,blank=True)

    def __unicode__(self):
        return self.name;

class pxelinuxcfg(models.Model):
    name          = models.CharField(max_length=80)
    configuration = models.CharField(max_length=20480)
    description   = models.CharField(max_length=300)

    def __unicode__(self):
        return self.name;


# client will contain a complete start.conf
# it has a timestamp to allow a backup via a copy operation
class client(models.Model):
    date           = models.BigIntegerField(default=int(format(datetime.now(), u'U')))
    ipaddr         = models.GenericIPAddressField(default='127.0.0.1')
    ipaddrint      = models.BigIntegerField(default=0)
    pxelinuxconfiguration = models.ForeignKey(pxelinuxcfg,blank=True)
    osentries      = models.ManyToManyField(os,blank=True)
    server         = models.CharField(max_length=20)
    cache          = models.CharField(max_length=80)
    smbdir         = models.CharField(max_length=80)
    autostarttimeout = models.IntegerField(default=20,blank=True)
    autostartos    = models.CharField(max_length=80,blank=True)
    autopartition  = models.BooleanField(default=True)
    autosync       = models.BooleanField(default=True)
    installmbr     = models.BooleanField(default=True)
    torrentenabled = models.BooleanField(default=False)
    template       = models.BooleanField(default=False)
    vms            = models.ManyToManyField(vm,blank=True)
    description    = models.CharField(max_length=300,blank=True)

    class Meta:
        ordering = ['ipaddrint']

    def __unicode__(self):
        return self.ipaddr;


class clientGroup(models.Model):
    name        = models.CharField(max_length=80)
    members     = models.ManyToManyField(client,blank=True)
    description = models.CharField(max_length=300,blank=True)

    def __unicode__(self):
        return self.description;

class diskAdmin(admin.ModelAdmin):
    list_display = ( 'device', )

class clientAdmin(admin.ModelAdmin):
    list_display = ( 'ipaddr', )

class clientGroupAdmin(admin.ModelAdmin):
    list_display = ( 'description', )

class pxelinuxcfgAdmin(admin.ModelAdmin):
    list_display = ( 'description', )

class partitionSelectionAdmin(admin.ModelAdmin):
    list_display = ( 'name', )

class partitionAdmin(admin.ModelAdmin):
    list_display = ( 'device', )
    
class osAdmin(admin.ModelAdmin):
    list_display = ('name', )

class vmAdmin(admin.ModelAdmin):
    list_display = ('name', )



admin.site.register(client, clientAdmin)
admin.site.register(clientGroup, clientGroupAdmin)
admin.site.register(pxelinuxcfg, pxelinuxcfgAdmin)
admin.site.register(partition, partitionAdmin)
admin.site.register(disk, diskAdmin)
admin.site.register(partitionSelection, partitionSelectionAdmin)
admin.site.register(os, osAdmin)
admin.site.register(vm, vmAdmin)

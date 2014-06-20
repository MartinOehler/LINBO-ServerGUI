// Author: Martin Oehler <oehler@knopper.net> 2013
// License: GPL V2

function save_changes() {

    var selected = document.getElementById('editorselector').value;
    data = $('#editorform').serialize();
    Dajaxice.linboweb.linboserver.saveform(Dajax.process,
                                             {'option':'Save',
                                              'selector':selected,
                                              'data':data});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selected});}, 500 );

    return false;  
};


// **************************************************************************
// Partition Selection, Partition
// **************************************************************************

function save_partitionselection() {

    var partitionselection = document.getElementById('partitionselectionselector').value;
    var selected = document.getElementById('editorselector').value;
    dataPartitionSelection = ''; 

    console.log(dataPartitionSelection);
    dataPartitions = $('#editorform').serialize();


    Dajaxice.linboweb.linboserver.save_partitionselection(Dajax.process,
                                             {'option':'Save',
                                              'selector':partitionselection,
                                              'dataPartitionSelection':dataPartitionSelection,
					      'dataPartitions':dataPartitions});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selected});}, 500 );

    return false;  
};

function remove_partition(partition) {

    var partitionselection = document.getElementById('partitionselectionselector').value;
    var selected = document.getElementById('editorselector').value;

    Dajaxice.linboweb.linboserver.remove_partition(Dajax.process,
						   {'selectedpartitionselection':partitionselection,
						    'selectedpartition':partition});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selected});}, 500 );							   
 
    return(false);
};

function remove_partitionselection() {

    var partitionselection = document.getElementById('partitionselectionselector').value;
    var selected = document.getElementById('editorselector').value;
    
    Dajaxice.linboweb.linboserver.remove_partitionselection(Dajax.process,
							    {'selectedpartitionselection':partitionselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selected});}, 500 );							   
 
    return(false);
};


// **************************************************************************
// VM
// **************************************************************************

function save_vm() {

    var vmselection = document.getElementById('vmselector').value;
    var selection = document.getElementById('editorselector').value;

    datavm = ''; 

    datavm = $('#editorform').serialize();

    Dajaxice.linboweb.linboserver.save_vm(Dajax.process,
                                          {'option':'Save',
                                           'selector':vmselection,
                                           'datavm':datavm});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );

    return false;  
};

function remove_vm() {

    var vmselection = document.getElementById('vmselector').value;
    var selection = document.getElementById('editorselector').value;

    Dajaxice.linboweb.linboserver.remove_vm(Dajax.process,
					    {'selectedvm':vmselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );							   
 
    return(false);
};

// **************************************************************************
// Client Group
// **************************************************************************

function save_clientGroup() {

    var cgselection = document.getElementById('clientGroupselector').value;
    var selection = document.getElementById('editorselector').value;

    datacg = ''; 

    datacg = $('#editorform').serialize();

    Dajaxice.linboweb.linboserver.save_clientGroup(Dajax.process,
						   {'option':'Save',
						    'selector':cgselection,
						    'dataClientGroup':datacg});
    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );

    return false;  
};

function remove_clientGroup() {

    var cgselection = document.getElementById('clientGroupselector').value;
    var selection = document.getElementById('editorselector').value;

    Dajaxice.linboweb.linboserver.remove_clientGroup(Dajax.process,
						     {'selectedclientGroup':cgselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );							   
 
    return(false);
};


// **************************************************************************
// OS
// **************************************************************************

function save_os() {

    var osselection = document.getElementById('osselector').value;
    var selection = document.getElementById('editorselector').value;

    dataos = ''; 

    dataos = $('#editorform').serialize();

    Dajaxice.linboweb.linboserver.save_os(Dajax.process,
                                          {'option':'Save',
                                           'selector':osselection,
                                           'dataos':dataos});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );

    return false;  
};

function remove_os() {

    var osselection = document.getElementById('osselector').value;
    var selection = document.getElementById('editorselector').value;

    Dajaxice.linboweb.linboserver.remove_os(Dajax.process,
					    {'selectedos':osselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );							   
 
    return(false);
};

// **************************************************************************
// pxelinuxcfg
// **************************************************************************

function save_pxelinuxcfg() {

    var pxelinuxcfgselection = document.getElementById('pxelinuxcfgselector').value;
    var selection = document.getElementById('editorselector').value;

    datapxelinuxcfg = ''; 

    datapxelinuxcfg = $('#editorform').serialize();

    Dajaxice.linboweb.linboserver.save_pxelinuxcfg(Dajax.process,
                                          {'option':'Save',
                                           'selector':pxelinuxcfgselection,
                                           'datapxelinuxcfg':datapxelinuxcfg});

    // reload editor element
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );	
    
    return false;  
};

function remove_pxelinuxcfg() {

    var pxelinuxcfgselection = document.getElementById('pxelinuxcfgselector').value;
    var selection = document.getElementById('editorselector').value;
 
    Dajaxice.linboweb.linboserver.remove_pxelinuxcfg(Dajax.process,
					    {'selectedpxelinuxcfg':pxelinuxcfgselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );	
						   
    return(false);
};

// **************************************************************************
// Client
// **************************************************************************

function save_client() {

    var clientselection = document.getElementById('clientselector').value;
    var selection = document.getElementById('editorselector').value;

    dataclient = ''; 

    dataclient = $('#editorform').serialize();

    Dajaxice.linboweb.linboserver.save_client(Dajax.process,
                                          {'option':'Save',
                                           'selector':clientselection,
                                           'dataclient':dataclient});


    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );

    return false;  
};

function remove_client() {

    var clientselection = document.getElementById('clientselector').value;
    var selection = document.getElementById('editorselector').value;

    Dajaxice.linboweb.linboserver.remove_client(Dajax.process,
					    {'selectedclient':clientselection});

    // update view
    setTimeout( function(){Dajaxice.linboweb.linboserver.displayeditor(Dajax.process, {'option':selection});}, 500 );							   
 
    return(false);
};



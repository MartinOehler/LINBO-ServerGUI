// Author: Martin Oehler <oehler@knopper.net> 2013
// License: GPL V2

function documentisready() {
    // build our page
    Dajaxice.linboweb.linboserver.loadImageAdminDiv(Dajax.process);

}

function checkMoveOperation() {
    var selected=$('#fileselectorincoming option:selected').val();
    var newname=$('#newfilename').val();

    var selectobject=document.getElementById("fileselectorcache");
    for (var i=0; i<selectobject.length; i++){
	// alert( selectobject.options[i].value );
	if( newname != '' ) {
	    if( selectobject.options[i].value == newname ) {
		alert('Name already existing, aborting!');
		return false;
	    }
	} else {
	    if( selectobject.options[i].value == selected ) {
		alert('Name already existing, aborting!');
		return false;
	    }
	}    
    }

    
    if( newname != '' ) {
	var answer = confirm("Really copy /var/linbo/incoming/"+selected+" to /var/linbo/cache/"+newname+"?");
	if (answer){
	    Dajaxice.linboweb.linboserver.moveFileIncomingToCache(Dajax.process,
								  {'filenameorig':selected,
								   'filenametarget':newname});
	}
    } else {
	var answer = confirm("Really copy /var/linbo/incoming/"+selected+" to /var/linbo/cache/ ?");
	if (answer){
	    newname=selected;
	    Dajaxice.linboweb.linboserver.moveFileIncomingToCache(Dajax.process,
								  {'filenameorig':selected,
								   'filenametarget':newname});

	}
    }
}

$(document).ready(documentisready());

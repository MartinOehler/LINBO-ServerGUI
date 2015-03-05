// Author: Martin Oehler <oehler@knopper.net> 2013
// License: GPL V2

// **************************************************************************
// Wizard
// **************************************************************************

function createClientFromTemplate() {

    var clientgroupselection = document.getElementById('clientgroupselector').value;
    var clienttemplateselection = document.getElementById('templateselector').value;
    var ipaddr = document.getElementById('newclientip').value;

    Dajaxice.linboweb.linboserver.createClientFromTemplate(Dajax.process,
							   {'clientgroupselection':clientgroupselection,
							    'clienttemplateselection':clienttemplateselection,
							    'ipaddr':ipaddr});

    return(false);
};

function addColumn(tblId)
{
	var tblHeadObj = document.getElementById(tblId).tHead;
	for (var h=0; h<tblHeadObj.rows.length; h++) {
		var newTH = document.createElement('th');
		tblHeadObj.rows[h].appendChild(newTH);
		newTH.innerHTML = 'Cost '  + (tblHeadObj.rows[h].cells.length - 2)
	}

	var tblBodyObj = document.getElementById(tblId).tBodies[0];
	for (var i=0; i<tblBodyObj.rows.length; i++) {
		var newCell = tblBodyObj.rows[i].insertCell(-1);
		element = document.createElement("input");
        element.type = "number";
        element.name = tblId ;
        element.step = "any";
		element.value = "0";
        newCell.appendChild(element);
	}
}

function deleteColumn(tblId)
{
	var allRows = document.getElementById(tblId).rows;
    
	for (var i=0; i<allRows.length; i++) {
		if (allRows[i].cells.length > 1) {
			allRows[i].deleteCell(-1);
		}
	}
}
function addRowToTable(tableID)
{
    var root = document.getElementById(tableID).getElementsByTagName('tbody')[0];
    var rows = root.getElementsByTagName('tr');
    
    var clone = cloneEl(rows[rows.length - 1]);
    
    root.appendChild(clone);

}
function cloneEl(el) {
    var clo = el.cloneNode(true);
    
    return clo;
}


function removeRow(oButton) {
    var tbl = document.getElementById('input-table');
    tbl.deleteRow(oButton.parentNode.parentNode.rowIndex);       // BUTTON -> TD -> TR.
}
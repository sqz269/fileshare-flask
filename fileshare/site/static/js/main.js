$(document).ready(initialize);

function initialize()
{
    setCurrentDirectory();
}

function setCurrentDirectory()
{
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        changeDirectory(currentPath);
    }
    else
    {
        changeDirectory("/");
    }
}

$("#check-all-folder").click(function(){
    $('input.check-dir:checkbox').not(this).not("#dir-selection").prop('checked', this.checked);
});

$("#check-all-file").click(function(){
    $('input.check-file:checkbox').not(this).not("#file-selection").prop('checked', this.checked);
});


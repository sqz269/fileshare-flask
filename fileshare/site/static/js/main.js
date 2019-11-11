$(document).ready ( function(){
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        changeDirectory(currentPath);
    }
    else
    {
        changeDirectory("/");
    }
});

$("#checkAll").click(function(){
    $("input[type=checkbox]").prop('checked', $(this).prop('checked'));
});

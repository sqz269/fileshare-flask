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
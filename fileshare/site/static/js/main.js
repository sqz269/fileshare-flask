$(document).ready ( function(){
    let currentPath = getUrlVars()["path"];
    console.log("Current Path is: " + currentPath)
    if (currentPath)
    {
        changeDirectory(currentPath);
    }
    else
    {
        changeDirectory("/");
    }
})
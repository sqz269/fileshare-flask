function changeDirectory()
{

}

function refresh()
{
    
}

function setURLCurrentDirectory(cPath)
{
    history.pushState({path: cPath}, "", `?path=${cPath}`)
}

function changeDirectory(dst)
{
    sendPostRequest(`/api/files?path=${dst}`, null, processFileResponse, undefined, undefined, dst);
}

function changeDirectoryParent()
{
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        let currentPathSplit = currentPath.split("/");
        let newPath = currentPathSplit.slice(0, currentPathSplit.length - 1).join("/")
        if (!newPath)
            newPath = "/"
        changeDirectory(newPath);
    }
    else
    {
        changeDirectory("/");
    }
}

function processFileResponse(status, resp, dirDst)
{
    if (status == 200)
    {
        removeAllDisplayedFiles();
        resp = JSON.parse(resp);
        let path = Object.keys(resp)[0];
        setURLCurrentDirectory(path);

        let totalDirCount = 0;
        let totalFileCount = 0;

        for (let dir in resp[path])
        {
            if (resp[path][dir].isDir)
            {
                fileContainerAddItem(dir, resp[path][dir].path, 'N/A', cvtUnixTimeToLocalTime(resp[path][dir].lastmod), true);
                totalDirCount++;
            }
        }

        for (let file in resp[path])
        {
            if (!resp[path][file].isDir)
            {
                fileContainerAddItem(file, resp[path][file].path, Math.round((resp[path][file].size / 1024)), cvtUnixTimeToLocalTime(resp[path][file].lastmod), false);
                totalFileCount++;
            }
        }

        setTotalDirAndFile(totalFileCount, totalDirCount);
    }
}

function refresh()
{

}

function setURLCurrentDirectory(cPath)
{
    history.pushState({path: cPath}, "", `?path=${cPath}`)
}

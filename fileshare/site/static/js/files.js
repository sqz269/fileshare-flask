/**
 * Change the url paramter "?path=" with out reload the page
 * 
 * @param {string} cPath current working directory
 */
function setURLCurrentDirectory(cPath)
{
    history.pushState({path: cPath}, "", `?path=${cPath}`);
}


/**
 * Processes response from a change directory response and sets the files/dir to display
 * which the reposes looks like
 *  { <directory>:
        {<fileName>: {
            "isDir": <isFileDir {bool}>,
            "path": <fileUrlPath {str}>,
            "size": <fileSize> {int},
            "lastmod": <fileLastModDate {unix timestamp}>
        }}
    }
 * 
 * @param {number} status The completed XHR status
 * @param {string} resp the stringified JSON Object that contains the file information
 */
function processFileResponse(status, resp)
{
    if (status === 200)
    {
        removeAllDisplayedFiles();
        resp = JSON.parse(resp);
        let path = Object.keys(resp)[0];
        setURLCurrentDirectory(path);

        let totalDirCount = 0;
        let totalFileCount = 0;

        for (let dir in resp[path])  // Loop though all files and check if they are a directory and show them first
        {
            if (resp[path][dir].isDir)
            {
                fileContainerAddItem(dir, resp[path][dir].path, "N/A", cvtUnixTimeToLocalTime(resp[path][dir].lastmod), true);
                totalDirCount++;
            }
        }

        for (let file in resp[path])  // then show all the remaining files
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

/**
 * Change current directory, a wrapper for sendRequest
 * Actually does nothing other than do a sendRequest function
 * 
 * @param {string} dst The destination directory
 */
function changeDirectory(dst)
{
    sendRequest(`/api/files?path=${dst}`, null, processFileResponse);
}

/**
 * Move to parent directory, similar to "cd .." command 
 */
function changeDirectoryParent()
{
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        let currentPathSplit = currentPath.split("/"); // Split the path to arrays
        let newPath = currentPathSplit.slice(0, currentPathSplit.length - 1).join("/"); // Join every segment of the path except for the last part
        if (!newPath)  // If the joined path is empty that means the parent path must be root
            newPath = "/";
        changeDirectory(newPath);
    }
    else
    {
        changeDirectory("/");
    }
}


function refresh()
{

}

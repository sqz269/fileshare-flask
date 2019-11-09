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
        resp = JSON.parse(resp);
        removeAllDisplayedFiles();
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
    else
    {
        resp = JSON.parse(resp);
        notifyUserError("Error", `Change directory failed with error code ${resp["status"]}. | Details: ${resp["details"]}`)
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


function newFolder()
{
    let newFolderName =  $("#new-folder-name").val();
    let newFolderPath = getUrlVars()["path"] + "/" + newFolderName;
    console.log(`New folder url path: ${newFolderPath}`);
    sendRequest(`/api/folders?path=${newFolderPath}`, null, newFolderCallback, null, "PUT");
}

function newFolderCallback(status, resp)
{
    console.log(`STATUS: ${status} | RESP: ${resp}`)
}


function uploadFile()
{
    let formData = new FormData();
    let $fileInputElement = $("#file-upload")[0];

    for (let i = 0; i < $fileInputElement.files.length; i++)
    {
        formData.append("File", $fileInputElement.files[i], $fileInputElement.files[i].name);        
    }

    let dst = getUrlVars()["path"];

    $.ajax({
        xhr: function()
        {
            let xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(e)
            {
                if (e.lengthComputable)
                {
                    let perc = Math.round(e.loaded / e.total) * 100;
                    console.log(`CURRENT PERC: ${perc}`);
                }
            });

            return xhr;
        },

        type: "PUT",
        url: `/api/files?path=${dst}`,
        data: formData,
        processData: false,
        contentType: false,
        success: function()
        {
            console.log("SUCCESS");
        },

        statusCode: 
        {
            401: function (xhr)
            {
                console.log("UNAUTHORIZED");
            },
            
            500: function (xhr)
            {
                console.log("INTERNAL SERVER ERROR");
            },

            0: function (xhr)
            {
                console.log("REQUEST ABORTED. UNKNOWN");
            }
        }
    });
}


function refresh()
{

}

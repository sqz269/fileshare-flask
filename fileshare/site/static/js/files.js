/**
 * Change the url paramter "?path=" with out reload the page
 *
 * @param {string} cPath current working directory
 */
function setURLCurrentDirectory(cPath)
{
    history.pushState({path: cPath}, "", `?path=${cPath}`);
}

function setUploadFileLabel()  // TODO: Truncate Long filename
{
    let fileInputElement = document.getElementById("file-upload");  // get file input element
    if ("files" in fileInputElement)   // if there are files selected
    {
        if (!fileInputElement.files.length) // if no files are selected
        {
            $("#file-upload-label").html("Choose file");
        }
        else  // if files are selected
        {
            let totalFiles = 0;
            for (let i = 0; i < fileInputElement.files.length; i++)  // Count files in total
            {
                let file = fileInputElement.files[i];
                totalFiles += 1;
            }
            if (totalFiles > 1)  // if there is more than one file selected
            {
                let firstFileName = fileInputElement.files[0].name;
                $("#file-upload-label").html(firstFileName + " and " + (totalFiles - 1) + " More");
            }
            else  // if only one files are selected
            {
                let firstFileName = fileInputElement.files[0].name;
                $("#file-upload-label").html(firstFileName);
            }
        }
    }
}

function newFolder()
{
    let name = $("#new-folder-name").val();
    let path = getUrlVars()["path"]; // path of Parent folder of the new folder
    sendRequest(`/api/folder?path=${path}&name=${name}`, null, newFolderCallBack, undefined, undefined, "PUT")
    $("#new-folder-modal").modal("hide");

    function newFolderCallBack(status, resp)
    {
        resp = JSON.parse(resp);
        if (status === 200)
        {
            notifyUserSuccess("Success", "Folder has been created");
        }
        else
        {
            notifyUserError("Error", `Failed to create a new folder [${resp["status"]}]. Details: ${resp["details"]}`);
        }
    }
}

function uploadFile()  // TODO: Display a progress bar
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
                    let percent = (e.loaded / e.total * 100).toFixed(2);
                    $("#upload-progress").attr("aria-valuenow", percent).css("width", percent + "%").text(percent + "%");
                    // console.log("Percent Loaded: " + percent)
                }
            });

            return xhr;
        },

        type: "PUT",
        url: `/api/file?path=${dst}`,
        data: formData,
        processData: false,
        contentType: false,
        success: function()
        {
            notifyUserSuccess("Success", "File uploaded successfully");
        },

        statusCode:
        {
            401: function (xhr)
            {
                // console.log("UNAUTHORIZED");
            },

            500: function (xhr)
            {
                // console.log("INTERNAL SERVER ERROR");
            },

            0: function (xhr)
            {
                // console.log("REQUEST ABORTED. UNKNOWN");
            }
        }
    });
}

/**
 * Goes up to previous directory. Similar to ..
 */
function changeDirectoryParent()
{
    let currentPath = getUrlVars()["path"];
    if (currentPath !== "/")
    {
        let currentPathSplit = currentPath.split("/");
        let parentPath = currentPathSplit.slice(0, currentPathSplit.length - 1).join("/"); // Join every segment of the path except for the last part

        if (!parentPath){parentPath = "/";}
        changeDirectory(parentPath);
    }
}

/**
 * lists a directory
 *
 * @param {string} dst the path of the directory to list
 * @param {boolean} pushHistory will the changed url be pushed to history (enabling back button to access last visited directory)
 */
function changeDirectory(dst, pushHistory=true)
{
    sendRequest(`/api/file?path=${dst}&type=table`, null, changeDirectoryCallback, {"pushHistory": pushHistory}, undefined, "GET");

    function changeDirectoryCallback(status, resp, params)
    {
        let response = JSON.parse(resp);
        if (status === 200)
        {
            for (let key in response)
            {
                if (response.hasOwnProperty(key))
                {
                    if (params["pushHistory"])
                    {
                        setURLCurrentDirectory(key);  // Key is the path of the changed directory, or parent path of current directory?
                    }
                    let files = response[key]["files"];
                    let directories = response[key]["dirs"];
                    $("#table-folders").bootstrapTable("load", directories);
                    $("#table-files").bootstrapTable("load", files);
                }
            }

            $('.ops-btn').click(function(e) {  // Prevent trigger bootstrap-table's click to select when clicking on the operation button
                e.stopPropagation();
            });
        }
        else
        {
            notifyUserError("Error", `Failed to change directory [${response["status"]}]. Reason: ${response["details"]}`);
        }
    }
}

function deleteItem()
{
    let selectionFolders = $("#table-folders").bootstrapTable("getSelections");
    let selectionFiles = $("#table-files").bootstrapTable("getSelections");
    $("#folder-delete-total").html(selectionFolders.length);
    $("#file-delete-total").html(selectionFiles.length);
    $("#delete-modal").modal("show");
}

function sendDeleteRequest()
{
    let selectionFolders = $("#table-folders").bootstrapTable("getSelections");
    let selectionFiles = $("#table-files").bootstrapTable("getSelections");

    let requestJson = {"file": [], "folder": []};
    for (let i = 0; i < selectionFolders.length; i++)
    {
        let item = selectionFolders[i];
        requestJson.folder.push(item.path);
    }

    for (let i = 0; i < selectionFiles.length; i++)
    {
        let item = selectionFiles[i];
        requestJson.file.push(item.path);
    }

    sendRequest("/api/file", JSON.stringify(requestJson), deleteRequestCallBack, undefined, undefined, "DELETE");

    function reloadWindow() {window.location.reload()}

    function deleteRequestCallBack(status, resp)
    {
        resp = JSON.parse(resp);
        if (status === 200)
        {
            notifyUserSuccessClickAction("Success", "Items has been deleted, Click Here to reload", reloadWindow);
        }
        else
        {
            notifyUserError("Error", `${resp["status"]} Failed to delete items due to ${resp['details']}`);
        }
    }
}

function renameFile()
{

}

function downloadFile(path, isFolder)
{
    if (isFolder)
    {
        sendRequest(`/api/folder/download?path=${path}`, null, downloadFolderCallback)

        function downloadFolderCallback(status, message)
        {
            if (status >= 200 || status <= 300)
            {
                let urlString = `/archive?path=${path}`;
                window.open(urlString, "_blank");
            }
        }
    }
    else
    {
        let urlString = path + "?mode=download";
        window.open(urlString, "_blank");
    }
}

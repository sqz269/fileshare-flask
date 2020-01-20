/**
 * Change the url paramter "?path=" with out reload the page
 * 
 * @param {string} cPath current working directory
 */
function setURLCurrentDirectory(cPath)
{
    let token = getUrlVars()["token"];
    if (token)
    {
        history.pushState({path: cPath}, "", `?path=${cPath}&token=${token}`);
    }
    else
    {
        history.pushState({path: cPath}, "", `?path=${cPath}`);
    }
}

function setUploadFileLabel()
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
                let firstFileName = fileInputElement.files[0].name
                $("#file-upload-label").html(firstFileName + " and " + (totalFiles - 1) + " More");
            }
            else  // if only one files are selected
            {
                let firstFileName = fileInputElement.files[0].name
                $("#file-upload-label").html(firstFileName);
            }
        }
    }
}

function newFolder()
{
    let name = $("#new-folder-name").val();
    let path = getUrlVars()["path"]; // path of Parent folder of the new folder
    sendRequest(`/api/folder?path=${path}&name=${name}`, null, newFolderCallBack, null, "PUT")
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
    if (currentPath != "/")
    {
        let currentPathSplit = currentPath.split("/");
        let parentPath = currentPathSplit.slice(0, currentPathSplit.length - 1).join("/"); // Join every segment of the path except for the last part

        if (!parentPath){parentPath = "/";}
        changeDirectory(parentPath);
    }
}


function changeDirectory(dst)
{
    sendRequest(`/api/file?path=${dst}&type=table`, null, changeDirectoryCallback);

    function changeDirectoryCallback(status, resp)
    {
        let data = resp;
        console.log("Breakpoint");
        let response = JSON.parse(data);
        for (let key in response)
        {
            setURLCurrentDirectory(key);  // Key is the path of the changed directory
            let files = response[key]["files"];
            let directories = response[key]["dirs"];
            $("#table-folders").bootstrapTable("load", directories);
            $("#table-files").bootstrapTable("load", files);
        }
    }
}


function showDeleteModal()
{
    let delete_folder = $("input.check-dir:checkbox:checked").map(function() {return this.value;}).get();
    let delete_file = $("input.check-file:checkbox:checked").map(function() {return this.value;}).get();

    $("#file-delete-total").html(delete_file.length);
    $("#folder-delete-total").html(delete_folder.length);

    $("#delete-modal").modal("show");
}



function deleteFile()
{
    let delete_folder = $("input.check-dir:checkbox:checked").map(function() {return this.value;}).get();
    let delete_file = $("input.check-file:checkbox:checked").map(function() {return this.value;}).get();

    let delete_json = {"folder": delete_folder, "file": delete_file};

    sendRequest("/api/folder", JSON.stringify(delete_json), deleteFileCallBack, "application/json", "DELETE");

    $("#delete-modal").modal("hide");

    function deleteFileCallBack(status, resp)
    {
        resp = JSON.parse(resp);   
        if (status === 200)
        {
            notifyUserSuccess("Success", resp["details"]);
        }
        else
        {
            notifyUserError("Error", resp["details"])
        }
    }
}

function renameFile()
{
    
}

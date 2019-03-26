function toLightTheme() 
{
    $(".bg-secondary").toggleClass("bg-secondary bg-light");
    $(".bg-dark").toggleClass("bg-dark bg-white");
    $(".text-light").toggleClass("text-light text-dark");
}


function toDarkTheme() 
{
    $(".bg-white").toggleClass("bg-white bg-dark");
    $(".bg-light").toggleClass("bg-light bg-secondary");
    $(".text-dark").toggleClass("text-dark text-light");
}


function readCookie(name) 
{
    var nameEQ = name + "=";
    var ca = document.cookie.split(";");
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)===" ") {
            c = c.substring(1,c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length,c.length);
        }
    }
    return null;
}


function switchTheme() 
{
    let themeSelect = $("#ChangeTheme");
    if (readCookie("theme") == "dark") {
        toLightTheme();
        document.cookie = "theme=light; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        themeSelect.html("Dark Theme");
    }
    else {
        toDarkTheme();
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        themeSelect.html("Light Theme");
    }
    return 0;
}

function cdParent() 
{
    window.location.replace("../");
}

function cdRoot() 
{
    window.location.replace("/");
}

window.onload = function() 
{
    // Set upload destination
    let dst = "/Upload?dst=" + encodeURIComponent(window.location.pathname)  // Maybe will add a dst chooser to file upload
    document.getElementById("uploadFileForm").action = dst;
    // LOAD User settings
    let theme = readCookie("theme");
    if (theme == null) {
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
    }
    else if (theme !== "dark"){
            toLightTheme();
            $("#ChangeTheme").html("Dark Theme");
    }

}

// Upload related functions (start)

function uploadStartChange()
{
    $("#UploadInfo").toggleClass("d-none d-block"); // show upload progress bar
    $("#UploadProgress").addClass("progress-bar-animated");  // Animate progress bar

    $("#UploadInfoFileView").toggleClass("d-none d-block"); // show upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // Animate progress bar

    $("#uploadFileSubmit").addClass("disabled").attr("value", "Uploading...");  // Disable upload button
    $("#uploadFileInput").attr("disabled", true);  // disable select file while uploading file
}

function uploadFinishChangeSuccess() 
{
    $("#bannerMessage").html("Your file has been successfully uploaded.");
    $("#operationSuccessBanner").toggleClass("d-none d-show");

    $("#UploadInfo").toggleClass("d-block d-none"); // hide upload progress bar
    $("#UploadProgress").removeClass("progress-bar-animated"); // remove animation on the progress bar

    $("#UploadInfoFileView").toggleClass("d-block d-none"); // hide upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // remove Animate progress bar

    $("#UploadProgress").attr("aria-valuenow", 0).css("width", 0 + "%").text(0 + "%");  // Reset the progress bar
    $("#uploadFileInput").attr("disabled", false);  // disable select file while uploading file
    $("#uploadFileSubmit").removeClass("disabled").attr("value", "Upload");  // Disable upload button
}

function uploadFinishChangeFailed() 
{
    $("#UploadInfo").toggleClass("d-block d-none"); // hide upload progress bar
    $("#UploadProgress").removeClass("progress-bar-animated"); // remove animation on the progress bar

    $("#UploadInfoFileView").toggleClass("d-block d-none"); // hide upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // remove Animate progress bar

    $("#UploadProgress").attr("aria-valuenow", 0).css("width", 0 + "%").text(0 + "%");  // Reset the progress bar
    $("#uploadFileInput").attr("disabled", false);  // disable select file while uploading file
    $("#uploadFileSubmit").removeClass("disabled").attr("value", "Upload");  // Disable upload button
}

function uploadFinishModalChangeFailed(errmsg) 
{
    $("#UploadStatusFailedText").html("Upload Failed: " +errmsg);
    $("#UploadStatusFailedText").toggleClass("d-none");
    uploadFinishChangeFailed();
}


function sendPOSTRequest(targetURL, data, callBackFunction, contentType="application/json")
{
    // Sending and receiving data using POST
    let xhr = new XMLHttpRequest();
    xhr.open("POST", targetURL, true);
    xhr.setRequestHeader("Content-Type", contentType);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            console.log(xhr.responseText);
            callBackFunction(xhr.responseText);
        }
    }
    xhr.send(data);
}


$(document).ready(function() {  // Credit to https://www.youtube.com/watch?v=f-wXTpbNWoM
	$("#uploadFileForm").on("submit", function(event) {
		event.preventDefault();

        var formData = new FormData($("form")[0]);

        uploadStartChange();

        let dst = encodeURIComponent(window.location.pathname);

		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener("progress", function(e) {

					if (e.lengthComputable) {

						// console.log("Bytes Loaded: " + e.loaded);
						// console.log("Total Size: " + e.total);
						// console.log("Percentage Uploaded: " + (e.loaded / e.total))

						let percent = Math.round((e.loaded / e.total) * 100);

                        $("#UploadProgress").attr("aria-vawaluenow", percent).css("width", percent + "%").text(percent + "%");
                        $("#UploadProgressFileView").attr("aria-vawaluenow", percent).css("width", percent + "%").text(percent + "%");
					}

				});

				return xhr;
			},
			type : "POST",
			url : "/Upload?dst=" + dst,
			data : formData,
			processData : false,
			contentType : false,
			success : function() {
                uploadFinishChangeSuccess();
                console.log("Operation Completed :" + xhr.statusCode);
            },
            complete: function(xhr, textStatus) {
                console.log("Operation Completed :" + xhr.statusCode);
            },
            statusCode: {
                401: function(xhr) {
                    uploadFinishModalChangeFailed("Authentication Required");
                    console.log("Operation Completed :" + xhr.statusCode);
                },
                500: function(xhr) {
                    uploadFinishModalChangeFailed("Server Unable To Handle Requests");
                    console.log("Operation Completed :" + xhr.statusCode);
                },
                0: function(xhr) {
                    uploadFinishModalChangeFailed("Request Aborted By Server");
                    console.log("Operation Completed :" + xhr.statusCode);
                }
              }
		});
	});
});

// Upload file related function (ends)

function moveFile()
{

}

function userLogin()
{

    function loginCallBack(resp){
        var authStatus = JSON.parse(resp);
        if (!authStatus["STATUS"]){
            $("#loginStatusSuccess").toggleClass("d-none d-show");
        }
        else {
            $("#loginStatusFail").toggleClass("d-none d-show");
        }
        console.log(authStatus);
    }

    let url = window.location.protocol + "//" + window.location.hostname + "/Login";
    let username = $("#loginInputUsername").val();
    let password = $("#loginInputPassword").val();
    if (username == "" || password == ""){
        $("#loginStatusFail").toggleClass("d-none d-show");
    }
    else {
        let data = JSON.stringify({"USERNAME": username, "PASSWORD": password});
        sendPOSTRequest(url, data, loginCallBack);
    }
}


function displayFileInfo(info) 
{
    // Show file info, can be replaced with for loop but too lazy :(
    $("#fileNameData").html(info.file_name);
    $("#fileExtData").html(info.file_ext);
    $("#filePathData").html(info.file_path);
    $("#fileLocationData").html(info.location);
    $("#modDateData").html(info.last_mod);
    $("#createDateData").html(info.created);
    $("#fileSizeData").html(info.file_size + " bytes");
    $("#fileContentTypeData").html(info.file_content_type);
    $("#detailedInfoData").html(info.full_detail);
    // Replace Open file url
    $("#openFile").attr("href", info.location);
    $("#openFileNewtab").attr("href", info.location);
    // Show modal
    $("#fileInfoModal").modal();
}

function getFileInfo(fileName) 
{
    function getFileInfoCallback(resp) {
        var json = JSON.parse(resp);
        displayFileInfo(json);
    }
    let currentPath = window.location.pathname;
    let url = window.location.protocol + "//" + window.location.hostname + "/ShowFileDetail";
    let data = JSON.stringify({"PATH": currentPath, "FILENAME": fileName});
    sendPOSTRequest(url, data, getFileInfoCallback);
}

function setUploadFileLabel() 
{
    let fileInputElement = document.getElementById("uploadFileInput");  // get file input element
    if ("files" in fileInputElement)   // if there are files selected
    {
        if (!fileInputElement.files.length) // if no files are selected
        {
            $("#fileToUpload").html("Choose file");
        }
        else  // if files are selected
        {
            let totalFiles = 0;
            for (let i = 0; i < fileInputElement.files.length; i++)  // Count files in total
            {
                let file = fileInputElement.files[i]; 
                totalFiles += 1;
            }
            console.log("Total files: " + totalFiles)
            if (totalFiles > 1)  // if there is more than one file selected
            { 
                let firstFileName = fileInputElement.files[0].name
                $("#fileToUpload").html(firstFileName + " and " + (totalFiles - 1) + " More");
            }
            else  // if only one files are selected
            {
                let firstFileName = fileInputElement.files[0].name
                $("#fileToUpload").html(firstFileName);
            }
        }
    }
}


function addCheckBoxFiles()
{
    let listItems = $(".CheckBoxHolder");
    listItems.each(function(idx, li) {
        let files = $(li);
        files.toggleClass("d-none d-block")
    });
}

function removeCheckBoxFiles()
{
    let listItems = $(".CheckBoxHolder");
    listItems.each(function(idx, li) {
        let files = $(li);
        files.toggleClass("d-block d-none");
    });
}

function uncheckCheckBoxFiles()
{
    let listItems = $(".CheckBoxHolder");
    listItems.each(function(idx, li) {
        let files = $(li);
        files.prop("checked", false);
    });
}


function getFilesToModify() 
{
    var filesToModify = []
    let listItems = $(".fileSelected");
    listItems.each(function(idx, li) {
        var files = $(li);
        $(files).data("targetPath");
        if ($(files).is(':checked')){
            filesToModify.push($(files).data("targetpath"));
        }
    });
    console.log(filesToModify);
    return filesToModify;
}

function appendModifyFilesToModal(modalUnorderedListID)
{
    emptyModalFileContent(modalUnorderedListID)
    let ULElement = $("#" + modalUnorderedListID);
    let filesToModify = getFilesToModify();
    for (let i in filesToModify)
    {
        ULElement.append('<li class="list-group-item bg-dark text-light tobeDeleted">' + filesToModify[i] + '</li>')
    }
}

function emptyModalFileContent(modalUnorderedListID)
{
    let ULElement = $("#" + modalUnorderedListID);
    ULElement.empty();
}

function moveFilePrepare()
{
    $("#MoveFileConfirm").toggleClass("d-none d-block");
    addCheckBoxFiles();
}


function moveFileExecute()
{
    function moveFileExecuteCallback(resp) {
        let json = JSON.parse(resp);

    }

    let modifyItems = getFilesToModify();
    let data = JSON.stringify({"FILES": modifyItems});
    let url = window.location.protocol + "//" + window.location.hostname + "/Move";
    sendPOSTRequest(url, data, moveFileExecuteCallback);
}


function moveFileCleanUp()
{
    $("#MoveFileConfirm").toggleClass("d-block d-none");
    removeCheckBoxFiles();
    uncheckCheckBoxFiles();
    emptyModalFileContent("fileToMove");
}


function deleteFilePrepare()
{
    $("#DeleteFileConfirm").toggleClass("d-none d-block");
    addCheckBoxFiles();
}

function deleteFileExecute()
{
    function deleteFileExecuteCallback(resp){
        console.log("Server Response: " + resp);
        let json = JSON.parse(resp);
        let status = json.STATUS;
        let details = json.Details;
        console.log("Status " + status);
        console.log("Details " + details)
        if (status != 0){
            $("#DeleteFileStatusFailedText").toggleClass("d-none d-show");
            $("#DeleteFileStatusFailedText").html(details);
        }
        else {
            $("#bannerMessage").html("Files has been deleted.");
            $("#operationSuccessBanner").toggleClass("d-none d-show");
        }
    }    

    let modifyItems = getFilesToModify();
    let data = JSON.stringify({"FILES": modifyItems});
    let url = window.location.protocol + "//" + window.location.hostname + "/Delete";
    sendPOSTRequest(url, data, deleteFileExecuteCallback);
}

function deleteFileCleanUp()
{
    $("#DeleteFileConfirm").toggleClass("d-block d-none")
    removeCheckBoxFiles();
    uncheckCheckBoxFiles();
    emptyModalFileContent("filesToDelete");
}


function makeDir()
{
    function makeDirCallBack(resp) {
        console.log("Server Response: " + resp);
        let json = JSON.parse(resp);
        let status = json.STATUS;
        let details = json.Details;
        console.log("Status " + status);
        console.log("Details " + details)
        if (status != 0){
            $("#MakeDIRStatusFailedText").toggleClass("d-none d-show");
            $("#MakeDIRStatusFailedText").html(details);
        }
        else {
            $("#bannerMessage").html("Directory has been created");
            $("#operationSuccessBanner").toggleClass("d-none d-show");
        }
    }

    let dir_name = $("#DirectoryNameInput").val();
    let dir_location = window.location.pathname + dir_name
    console.log(dir_location)
    let data = JSON.stringify({"DIR": [dir_location]});
    let url = window.location.protocol + "//" + window.location.hostname + "/Mkdir";
    sendPOSTRequest(url, data, makeDirCallBack)
}

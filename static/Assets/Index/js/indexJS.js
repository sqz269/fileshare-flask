function toLightTheme() {
    $(".bg-secondary").toggleClass("bg-secondary bg-light");
    $(".bg-dark").toggleClass("bg-dark bg-white");
    $(".text-light").toggleClass("text-light text-dark");
}


function toDarkTheme() {
    $(".bg-white").toggleClass("bg-white bg-dark");
    $(".bg-light").toggleClass("bg-light bg-secondary");
    $(".text-dark").toggleClass("text-dark text-light");
}


function readCookie(name) {
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


function switchTheme() {
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

function cdParent() {
    window.location.replace("../");
}

function cdRoot() {
    window.location.replace("/");
}

window.onload = function() {
    // Set upload destination
    let dst = "/Upload?dst=" + encodeURIComponent(window.location.pathname)
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

function uploadStartChange(){
    $("#UploadInfo").toggleClass("d-none d-block"); // show upload progress bar
    $("#UploadProgress").addClass("progress-bar-animated");  // Animate progress bar

    $("#UploadInfoFileView").toggleClass("d-none d-block"); // show upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // Animate progress bar

    $("#uploadFileSubmit").addClass("disabled").attr("value", "Uploading...");  // Disable upload button
    $("#uploadFileInput").attr("disabled", true);  // disable select file while uploading file
}

function uploadFinishChangeSuccess() {
    $("#fileUploadSuccessBanner").toggleClass("d-none d-show");

    $("#UploadInfo").toggleClass("d-block d-none"); // hide upload progress bar
    $("#UploadProgress").removeClass("progress-bar-animated"); // remove animation on the progress bar

    $("#UploadInfoFileView").toggleClass("d-block d-none"); // hide upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // remove Animate progress bar

    $("#UploadProgress").attr("aria-valuenow", 0).css("width", 0 + "%").text(0 + "%");  // Reset the progress bar
    $("#uploadFileInput").attr("disabled", false);  // disable select file while uploading file
    $("#uploadFileSubmit").removeClass("disabled").attr("value", "Upload");  // Disable upload button
}

function uploadFinishChangeFailed() {
    $("#UploadInfo").toggleClass("d-block d-none"); // hide upload progress bar
    $("#UploadProgress").removeClass("progress-bar-animated"); // remove animation on the progress bar

    $("#UploadInfoFileView").toggleClass("d-block d-none"); // hide upload progress bar on the file view page
    $("#UploadProgressFileView").addClass("progress-bar-animated");  // remove Animate progress bar

    $("#UploadProgress").attr("aria-valuenow", 0).css("width", 0 + "%").text(0 + "%");  // Reset the progress bar
    $("#uploadFileInput").attr("disabled", false);  // disable select file while uploading file
    $("#uploadFileSubmit").removeClass("disabled").attr("value", "Upload");  // Disable upload button
}

function uploadFinishModalChangeFailed(errmsg) {
    $("#UploadStatusFailedText").html("Upload Failed: " +errmsg);
    $("#UploadStatusFailedText").toggleClass("d-none");
    uploadFinishChangeFailed();
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


function move_file()
{
    // Sending and receiving data in JSON format using POST method
    let xhr = new XMLHttpRequest();
    let url = window.location.protocol + "//" + window.location.hostname + "/Move";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var authStatus = JSON.parse(xhr.responseText);
            if (authStatus["STATUS"] === 0){
                $("#loginStatusSuccess").toggleClass("d-none d-show");
            }
            else {
                $("#loginStatusFail").toggleClass("d-none d-show");
            }
            console.log(authStatus);
        }
    };

    var data = JSON.stringify({"USERNAME": username, "PASSWORD": password});
    console.log(data);
    xhr.send(data);
}

function user_login()
{
    let currentPath = window.location.pathname;
    // Sending and receiving data in JSON format using POST method
    let xhr = new XMLHttpRequest();
    let url = window.location.protocol + "//" + window.location.hostname + "/Login";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var authStatus = JSON.parse(xhr.responseText);
            if (authStatus["STATUS"] === 0){
                $("#loginStatusSuccess").toggleClass("d-none d-show");
            }
            else {
                $("#loginStatusFail").toggleClass("d-none d-show");
            }
            console.log(authStatus);
        }
    };

    let username = $("#loginInputUsername").val();
    let password = $("#loginInputPassword").val();

    if (username == "" || password == ""){
        $("#loginStatusFail").toggleClass("d-none d-show");
    }
    else {
        var data = JSON.stringify({"USERNAME": username, "PASSWORD": password});
        console.log(data);
        xhr.send(data);
    }
}


function displayFileInfo(info) {
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

function getFileInfo(fileName) {
    let currentPath = window.location.pathname;
    // Sending and receiving data in JSON format using POST method
    let xhr = new XMLHttpRequest();
    let url = window.location.protocol + "//" + window.location.hostname + "/ShowFileDetail";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            displayFileInfo(json);
        }
    };
    var data = JSON.stringify({"PATH": currentPath, "FILENAME": fileName});
    xhr.send(data);
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

function toLightTheme() {
    $(".bg-secondary").toggleClass("bg-secondary bg-light")
    $(".bg-dark").toggleClass("bg-dark bg-white")
    $(".text-light").toggleClass("text-light text-dark")
}


function toDarkTheme() {
    $(".bg-white").toggleClass("bg-white bg-dark")
    $(".bg-light").toggleClass("bg-light bg-secondary")
    $(".text-dark").toggleClass("text-dark text-light")
}


function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1,c.length);
        }
        if (c.indexOf(nameEQ) == 0) {
            return c.substring(nameEQ.length,c.length);
        }
    }
    return null;
}


function switchTheme() {
    theme_select = $("#ChangeTheme")
    if (readCookie("theme") == "dark") {
        toLightTheme();
        document.cookie = "theme=light; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        theme_select.html("Dark Theme");
    }
    else {
        toDarkTheme();
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        theme_select.html("Light Theme");
    }
    return 0;
}

function cd_parent() {
    window.location.replace("../");
}

function cd_root() {
    window.location.replace("/");
}

window.onload = function() {
    // LOAD User settings
    let theme = readCookie("theme");
    if (theme == null) {
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
    }
    else {
        if (theme != "dark") {
            toLightTheme();
            $("#ChangeTheme").html("Dark Theme");
        }
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
    $("#fileTypeData").html(info.file_type);
    $("#detailedInfoData").html(info.full_detail);
    // Replace Open file url
    $("#openFile").attr("href", info.location);
    // Show modal
    $("#fileInfoModal").modal()
}

function getFileInfo(fileName) {
    let current_path = window.location.pathname;
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
    var data = JSON.stringify({"PATH": current_path, "FILENAME": fileName});
    xhr.send(data);
}

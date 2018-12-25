function to_light_theme() {
    $(".bg-secondary").toggleClass("bg-secondary bg-light")
    $(".bg-dark").toggleClass("bg-dark bg-white")
    $(".text-light").toggleClass("text-light text-dark")
}


function to_dark_theme() {
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


function switch_theme() {
    theme_select = document.getElementById("ChangeTheme")
    if (readCookie("theme") == "dark") {
        to_light_theme();
        document.cookie = "theme=light; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        theme_select.innerHTML = "Dark Theme";
    }
    else {
        to_dark_theme();
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
        theme_select.innerHTML = "Light Theme";
    }
    return 0;
}

function cd_parent() {
    let current_path = window.location.pathname;
    let path_split = current_path.split("/");
    let path_parent = path_split.slice(0, path_split.length - 1);
    window.location.replace(path_parent.join("/"));
}

function cd_root() {
    window.location.replace("/");
}

function test() {
    console.log("Test")
}


window.onload = function() {
    // LOAD User settings
    let theme = readCookie("theme");
    if (theme == null) {
        document.cookie = "theme=dark; expires=Thu, 18 Dec 2037 12:00:00 UTC;path=/";
    }
    else {
        if (theme != "dark") {
            to_light_theme();
            document.getElementById("ChangeTheme").innerHTML = "Dark Theme";
        }
    }
}

function addFileToDisplay(name, path, size, lastmod, mimetype, elementToAppend="#file-container")
{
    let $templateElement = $("#file-template").clone(false);
    $templateElement.removeAttr("id");
    $templateElement.find("#file-selection").attr("value", path).removeAttr("id");
    $templateElement.find("#file-name").attr("href", `${path}`).html(name).removeAttr("id");
    $templateElement.find("#file-newtab").attr("href", `${path}`).removeAttr("id");
    $templateElement.find("#file-lastmod").html(cvtUnixTimeToLocalTime(lastmod)).removeAttr("id");
    $templateElement.find("#file-size").html(size / 1024).removeAttr("id");
    $templateElement.find("#file-mime").html(mimetype).removeAttr("id");
    $templateElement.addClass("file-entry");
    $templateElement.appendTo(elementToAppend);
}

function addDirectoryToDisplay(name, path, size, lastmod, file_count, dir_count, elementToAppend="#folder-container")
{
    let $templateElement = $("#dir-template").clone(false);
    $templateElement.removeAttr("id");
    $templateElement.find("#dir-selection").attr("value", path).removeAttr("id");
    $templateElement.find("#dir-name").attr("href", `javascript:changeDirectory("${path}");`).html(name).removeAttr("id");
    $templateElement.find("#dir-size").html(size  / 1024).removeAttr("id");
    $templateElement.find("#dir-lastmod").html(cvtUnixTimeToLocalTime(lastmod)).removeAttr("id");
    $templateElement.find("#dir-content-file-count").html(file_count).removeAttr("id");
    $templateElement.find("#dir-content-dir-count").html(dir_count).removeAttr("id");
    $templateElement.addClass("directory-entry");
    $templateElement.appendTo(elementToAppend);
}

function addFileToDisplay(name, path, size, lastmod, mimetype, elementToAppend="#file-container")
{
    let $templateElement = $("#file-template").clone(false);
    $templateElement.removeAttr("id");
    $templateElement.find("#t-name").attr("href", `${path}`).html(name).removeAttr("id");
    $templateElement.find("#t-last-mod").html(cvtUnixTimeToLocalTime(lastmod)).removeAttr("id");
    $templateElement.find("#t-size").html(size / 1024).removeAttr("id");
    $templateElement.find("#t-mime").html(mimetype).removeAttr("id");

    $templateElement.find("#t-op-download").attr('href', `${path}?mode=download`).removeAttr("id");;
    $templateElement.find("#t-op-newtab").attr('href', `${path}`).removeAttr("id");;
    $templateElement.find("#t-op-rename").attr('href', ``).removeAttr("id");
    $templateElement.find("#t-op-delete").attr('href', ``).removeAttr("id");
    $templateElement.find("#t-op-move").attr('href', ``).removeAttr("id");

    $templateElement.addClass("file-entry");
    $templateElement.appendTo(elementToAppend);
}

function addDirectoryToDisplay(name, path, size, lastmod, file_count, dir_count, elementToAppend="#folder-container")
{
    let $templateElement = $("#dir-template").clone(false);
    $templateElement.removeAttr("id");
    $templateElement.find("#t-name").attr("href", `javascript:changeDirectory("${path}");`).html(name).removeAttr("id");
    $templateElement.find("#t-last-mod").html(size  / 1024).removeAttr("id");
    $templateElement.find("#t-size").html(cvtUnixTimeToLocalTime(lastmod)).removeAttr("id");
    $templateElement.find("#t-contents-folder").html(file_count).removeAttr("id");
    $templateElement.find("#t-contents-file").html(dir_count).removeAttr("id");

    $templateElement.find("#t-op-download").attr('href', `${path}?mode=download`).removeAttr("id");;
    $templateElement.find("#t-op-newtab").attr('href', `${path}`).removeAttr("id");;
    $templateElement.find("#t-op-rename").attr('href', ``).removeAttr("id");
    $templateElement.find("#t-op-delete").attr('href', ``).removeAttr("id");
    $templateElement.find("#t-op-move").attr('href', ``).removeAttr("id");


    $templateElement.addClass("directory-entry");
    $templateElement.appendTo(elementToAppend);
}

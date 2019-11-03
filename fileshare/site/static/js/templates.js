function fileContainerAddItemEx(fname, fpath, size, lastMod, isDir, elementToAppend)
{
    $templateElement = $("#file-template").clone(false);
    $templateElement.removeAttr("id");
    $templateElement.find("#file-selection").attr("value", fname).removeAttr("id");

    if (isDir)
        $img = $("#img-dir").clone(false).removeAttr("id")
    else
        $img = $("#img-file").clone(false).removeAttr("id")
    $templateElement.find("#file-type").append($img).removeAttr("id");

    $templateElement.find("#file-name").attr("href", fpath).html(fname).removeAttr("id");
    $templateElement.find("#file-lastmod").html(lastMod).removeAttr("id");
    $templateElement.find("#file-size").html(size).removeAttr("id");
    $templateElement.find("#file-operation-newtab").attr("href", fpath).removeAttr("id");
    $templateElement.appendTo(elementToAppend);
}

function fileContainerAddItem(fname, fpath, size, lastMod, isDir)
{
    fileContainerAddItemEx(fname, fpath, size, lastMod, isDir, "#file-container")
}

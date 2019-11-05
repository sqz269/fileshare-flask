/**
 * Create a new file item from #file-template and add it too an element
 *
 * @param {string} fname the file name
 * @param {string} fpath file path
 * @param {number} size the size of the file (cosmetic purpose only)
 * @param {string} lastMod the last modification date of the file (cosmetic purpose only)
 * @param {boolean} isDir is the file a directory (corresponding icons will be applies depend on the type)
 * @param {Selector} elementToAppend a jquery selector that points to the table the element will be appended to
 *                                   Default value is #file-container
 */
function fileContainerAddItem(fname, fpath, size, lastMod, isDir, elementToAppend="#file-container")
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


/**
 * Set total files and dirs number to display
 *
 * @param {number} totalFile total file this directory contains
 * @param {number} totalDir total directorys this dir contains
 */
function setTotalDirAndFile(totalFile, totalDir)
{
    $("#file-count").html(totalFile);
    $("#dir-count").html(totalDir);
}

/**
 * Remove all displayed file from the table except for the row with return to parent dir
 */
function removeAllDisplayedFiles()
{
    $("#file-container").find("tr:gt(0)").remove();
}

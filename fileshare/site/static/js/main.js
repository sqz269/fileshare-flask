$(document).ready(initialize);

function initialize()
{
    setCurrentDirectory();
}

function processBreadCrumb()
{
    let currentPath = getUrlVars()["path"];

}

function setCurrentDirectory(pushState=true)
{
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        changeDirectory(currentPath, pushState);
    }
    else
    {
        changeDirectory("/", pushState);
    }
}

(function() {

	if (window.history && window.history.pushState) {

		$(window).on('popstate', function() {
            console.log("Popped State. Current PATH VAR " + getUrlVars()["path"]);
            setCurrentDirectory(false);
		});
	}
})();

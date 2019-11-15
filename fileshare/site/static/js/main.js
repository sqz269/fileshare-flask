$(document).ready (initialize);


function initialize()
{
    retrieveServerSettings();
}


function retrieveServerSettings()
{
    sendRequest("/api/access-token", null, retrieveServerSettingsCallback, undefined, "OPTION");
}

var cfgAllowTokenUrlParam = undefined;
var cfgUserIssuedToken = undefined;
var cfgTokenIssueLoginRequired = undefined;

function retrieveServerSettingsCallback(status, resp)
{
    console.log(resp);
    resp = JSON.parse(resp);

    cfgAllowTokenUrlParam = resp["token_in_url_param"];
    cfgUserIssuedToken = resp["cfgUserIssuedToken"];
    cfgTokenIssueLoginRequired = resp["user_issue_token_require_auth"];

    let linkAccessTokenDisabled = false;
    let linkShareAccessTokenDisabled = false;

    if (!cfgAllowTokenUrlParam)
    {
        $("#file-copy-token").addClass("d-none");
        linkAccessTokenDisabled = true;
    }

    if (!cfgUserIssuedToken)
    {
        $("#file-share-token").addClass("d-none");
        linkShareAccessTokenDisabled = true;
    }

    if (cfgTokenIssueLoginRequired)
    {
        if (!isLoggedIn())
        {
            $("#file-share-token").addClass("d-none");
            linkShareAccessTokenDisabled = true;
        }
    }

    if (linkShareAccessTokenDisabled && linkAccessTokenDisabled)
    {
        $("#file-option-divi").addClass("d-none");
    }

    setInitialDirectory(); // Prevent Race condition
}


function setInitialDirectory()
{
    let currentPath = getUrlVars()["path"];
    if (currentPath)
    {
        changeDirectory(currentPath);
    }
    else
    {
        changeDirectory("/");
    }
}

$("#checkAll").click(function(){
    $("input[type=checkbox]").prop("checked", $(this).prop("checked"));
});

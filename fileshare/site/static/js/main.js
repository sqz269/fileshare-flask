$(document).ready (initialize);


function initialize()
{
    setInitialDirectory();
    retrieveServerSettings();
}


function retrieveServerSettings()
{
    sendRequest("/api/access-token", null, retrieveServerSettingsCallback, undefined, "OPTION");
}

var allow_token_url_param = undefined;
var user_issued_token = undefined;
var login_required_token_issue = undefined;

function retrieveServerSettingsCallback(status, resp)
{
    console.log(resp);
    resp = JSON.parse(resp);

    allow_token_url_param = resp["token_in_url_param"];
    user_issued_token = resp["user_issued_token"];
    login_required_token_issue = resp["user_issue_token_require_auth"];

    let linkAccessTokenDisabled = false;
    let linkShareAccessTokenDisabled = false;

    if (!allow_token_url_param)
    {
        $("#file-copy-token").addClass("d-none");
        linkAccessTokenDisabled = true;
    }

    if (!user_issued_token)
    {
        $("#file-share-token").addClass("d-none");
        linkShareAccessTokenDisabled = true;
    }

    if (login_required_token_issue)
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
    $("input[type=checkbox]").prop('checked', $(this).prop('checked'));
});

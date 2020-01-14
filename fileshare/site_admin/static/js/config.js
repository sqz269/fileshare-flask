function fetchConfig()
{
    sendRequest("/api/admin/configuration/all", null, fetchConfigCallBack, null, "GET")

    function fetchConfigCallBack(status, data)
    {
        let resp = JSON.parse(data);
        if (status === 200)
        {

        }
        else
        {
            notifyUserError("Error", `Failed to retrieve server configuration: ${data["details"]}`)
        }
    }
}

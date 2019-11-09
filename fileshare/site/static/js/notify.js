function notifyUserError(heading, message)
{
    Lobibox.notify("error", {
        title: heading,
        msg: message,
        sound: false,
        position: 'top right',
        continueDelayOnInactiveTab: false,
        pauseDelayOnHover: true,
        icon: false
    });
}

function notifyUserSuccess(heading, message)
{
    Lobibox.notify("success", {
        title: heading,
        msg: message,
        sound: false,
        position: 'top right',
        continueDelayOnInactiveTab: false,
        pauseDelayOnHover: true, 
        icon: false
    });
}

function _notifyBase(type, heading, message, onclick=undefined)
{
    Lobibox.notify(type, {
        title: heading,
        msg: message,
        sound: false,
        position: "top right",
        continueDelayOnInactiveTab: false,
        pauseDelayOnHover: true,
        icon: false,
        onClick: onclick
    });
}

function notifyUserError(heading, message)
{
    _notifyBase("error", heading, message);
}

function notifyUserSuccess(heading, message)
{
    _notifyBase("success", heading, message);
}

function notifyUserErrorClickAction(heading, message, onClickFunction)
{
    _notifyBase("error", heading, message, onClickFunction);
}

function notifyUserSuccessClickAction(heading, message, onClickFunction)
{
    _notifyBase("error", heading, message, onClickFunction);
}

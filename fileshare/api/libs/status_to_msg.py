STATUS_TO_MESSAGE = {
    0: "Success",
    1: "Feature Not in use",
    2: "Required paramater is not provided",
    3: "Invalid Password",
    4: "Access Token is invalid",
    5: "Login Token is invalid",
    6: "Login or Access Token is invalid",

    100: "Resource with the same name already exist",
    101: "Access to resource has been denied by the Operating System",
    102: "Illegal Path has been provided",
    103: "Target File/Folder does not exist"
}

STATUS_TO_HTTP_CODE = {
    0: 200,
    1: 400,
    2: 400,
    3: 401,
    4: 401,
    5: 401,
    6: 401,

    100: 409,
    101: 500,
    102: 100,
    103: 404
}

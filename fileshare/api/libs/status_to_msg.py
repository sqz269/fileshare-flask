class STATUS_ENUM:
    SUCCESS = 0
    FEATURE_DISABLED = 1
    MISSING_PARAMATER = 2
    INVALID_PASSWORD = 3
    INVALID_ACCESS_TOKEN = 4
    INVALID_LOGIN_TOKEN = 5

    RESOURCE_ALREADY_EXISTS = 100
    RESOURCE_ACCESS_DENIED = 101
    RESOURCE_INVALID_PATH = 102
    RESOURCE_MISSING = 103
    RESOURCE_ILLEGAL_PARAM = 104

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
    103: "Target File/Folder does not exist",
    104: "Illegal Paramater has been provided"
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
    102: 400,
    103: 404,
    104: 400
}

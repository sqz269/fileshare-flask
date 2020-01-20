/**
 * Send a XHR Request to a specific url with data
 * @param {string} url the URL to send the XHR Request to
 * @param {object} data the data that will be send with the request
 * @param {Function} callBack the function that will be called upon the XHR is done
 * @param {string} contentType the Conetent-Type header value (default application/json)
 * @param {string} method the method of the requestion (POST, DELETE etc.) (default POST)
 */
function sendRequest(url, data, callBack, contentType = "application/json", method = "POST")
{
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader("Content-Type", contentType);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            callBack(xhr.status, xhr.responseText);
        }
    };
    xhr.send(data);
}

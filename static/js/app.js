function tryHandleAuthError(jqXHR) {
    if (jqXHR.status == 401) {
        window.location.href = "/auth/login/"
    }
}

function showError(jqXHR) {

}
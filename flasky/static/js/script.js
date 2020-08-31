ClassicEditor
        .create(document.querySelector('#editor'))
        .catch(error => {}
    );


// ReCAPTCHA form submits
function onRegisterSubmit(token) {
    document.getElementById("register-form").submit();
}
function onLoginSubmit(token) {
    document.getElementById("login-form").submit();
}
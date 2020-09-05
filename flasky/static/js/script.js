ClassicEditor
        .create(document.querySelector('#editor'))
        .catch(error => {}
    );
$(function () {
        $("#udash-table").DataTable({
            "responsive": true,
            "autoWidth": false,
        });
    });

// ReCAPTCHA form submits
function onRegisterSubmit(token) {
    document.getElementById("register-form").submit();
}
function onLoginSubmit(token) {
    document.getElementById("login-form").submit();
}
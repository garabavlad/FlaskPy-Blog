$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });


    $('#sidebarCollapse').on('click', function () {
        // open or close navbar
        $('#sidebar').toggleClass('active');
        $('.udash-content').toggleClass('fullscreen');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

    $('.udash-close-arrow').on('click', function () {
        // open or close navbar
        $('#sidebar').toggleClass('active');
        $('.udash-content').toggleClass('fullscreen');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');

    });

});
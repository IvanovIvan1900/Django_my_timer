$(document).on('focus', '.select2-selection.select2-selection--single', function(e) {
    $(this).closest(".select2-container").siblings('select:enabled').select2('open');
});

// steal focus during close - only capture once and stop propogation
$('select.select2').on('select2:closing', function(e) {
    $(e.target).data("select2").$selection.one('focus focusin', function(e) {
        e.stopPropagation();
    });
});
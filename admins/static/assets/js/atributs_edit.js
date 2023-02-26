$(document).on('click', '.new_options_delete.local', (e) => {
    $(e.target).parent().parent().parent().remove()
    $('input[name="options_count"]').val(Number($('input[name="options_count').val()) - 1)
    $('.del-opt-container').last().html('<a class="btn btn-sm btn-danger ms-3 new_options_delete local"><i class="fe fe-trash" style="pointer-events: none;"></i></a>')
})
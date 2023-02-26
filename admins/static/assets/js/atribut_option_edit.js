$('.atribut_options').on('click', (e) => {
    let id = $(e.target).attr('data-id')
    let url = $(e.target).attr('data-get')
    $('#option_name_error').html('')

    $.ajax({
        url: url,
        type: 'GET',
        data: {'id': id},
        datatype: 'json',
        success: (data) => {
            console.log(data)
            for(let key in data) {
                if (String(key) != 'id') {
                    $(`[name="name#${key}"]`).val(data[String(key)])
                } else {
                    $('[name="id"]').val(data[String(key)])
                }
            }
        }
    })
})


$('#option-edit-form').on('submit', (e) => {
    e.preventDefault()
    let data = $(e.target).serialize()
    console.log(data)
    let url = `atribut_options/edit`
    console.log(data)

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        datatype: 'json',
        success: (data) => {
            console.log(data)
            $('#atributOptionModal').modal('hide')
        }
    })


})
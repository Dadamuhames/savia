$(document).on('click', '.delete_variant_btn.no-ajax', (e) => {
    console.log($(e.target).parent().parent())
    $(e.target).parent().parent().parent().remove()
    let last_id = $('.del_btn_container').last().attr('data-item')
    $('.del_btn_container').last().html(
        `
            <span class="delete_variant_btn no-ajax" data-id="${last_id}">&#215;</span>
        `
    )
    $('input[name="variant_count"]').val(Number($('input[name="variant_count"]').val()) - 1)
})

let category_atributs;

function fill_atributs(wrap, data) {
    $(wrap).html('')
    let item_id = $(wrap).attr('data-item')
    for (let item of data) {
        console.log(item)
        wrap.insertAdjacentHTML('beforeend', `
                        <div class="input_box">
                            <label for="price">${item.name}</label>
                            <select name="option[${item_id}]" id="options_${item_id}_${item.id}" class='form-select'></select>
                        </div>
                    `)
        for (let opt of item.options) {
            $(`#options_${item_id}_${item.id}`).html(
                $(`#options_${item_id}_${item.id}`).html() +
                `
                    <option value="${opt.id}" >${opt.name}</option>
                 `
            )
        }
    }
}

$(document).on('change', '#product_ctg_select', (e) => {
    let id = $(e.target).val()
    let url = '/admin/get_ctg_atributs'
    
    if(id == '') {
        return;
    }

    $.ajax({
        url: url,
        type: 'GET',
        data: {'id': id},
        success: (data) => {
            category_atributs = data;
            console.log(data)
            let atr_wraps = document.querySelectorAll('.atributs_wrap')
            console.log(atr_wraps)
            for (let wrap of atr_wraps) {
                fill_atributs(wrap, data)
            }
        }
    })
})


$(document.body).on("change", '.image_input', (e) => {
    const reader = new FileReader();
    reader.onload = () => {
        const uploaded_image = reader.result;
        const img_box = $(e.target).parent().find('.display-image');
        img_box.addClass("active");
        $(e.target).parent().find(".delete_img").addClass("active")
        img_box[0].style.backgroundImage = `url(${uploaded_image})`;
    }
    reader.readAsDataURL(e.target.files[0]);
})


function deleteImage(e) {
    $(e.target).parent().find('.image_input').val('')
    $(e.target).parent().find('.display-image').removeClass("active")
    $(e.target).removeClass('active')
}

$(document.body).on('click', '.delete_img.no-ajax', (e) => {
    deleteImage(e)
})



$(document).on('change', '.is_default', (e) => {
    for (let check of $('.is_default')) {
        check.checked = false
    }
    e.target.checked = true
})


$(document).on('change', '.ctg_select', () => {
    console.log('9')
    document.querySelector('.messages').insertAdjacentHTML('beforeEnd', '<div class="alert alert-danger message" role="alert"> Внимание! При изменении категории все добавленные вами ранее вариации будут удалены! </div>')
    
    setTimeout(() => {
        console.log($('.message'))
        $('.message').last().remove()
    }, 5000)
})



$(document).on('submit', 'form', (e) => {
    if ($('#product_ctg_select').val() == '') {
        e.preventDefault()
        $('#ctg_error').css('display', 'block')
    }
})
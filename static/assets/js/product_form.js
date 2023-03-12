$(document).on('change', '#product_ctg_select', (e) => {
    console.log($('.product_ctg_select'))
    id = $(e.target).val()
    $.ajax({
        url: '/admin/get_post_ctg',
        type: 'GET',
        data: {'id': id},
        success: (data) => {
            console.log(data)
            $("#post_ctg_wrap").html(`
                <div class="form-group">
                    <!-- Label  -->
                    <label class="form-label">
                        Пост категория
                    </label>
                    <br>
                    <!-- Input -->
                    <select name="category" class="form-control ctg_select product_ctg_select" id="post_ctg" class="form-control" name="category" data-choices>
                        <option value="">-----</option>
                    </select>
                </div>
            `)

            for(let ctg of data.categories) {
                $('#post_ctg').html($(`#post_ctg`).html() + `
                    <option value = "${ ctg.id }">${ ctg.name }</option>
                `)
            }
        } 
    })
})


$(document).on("change", '#post_ctg', (e) => {     
    id = $(e.target).val()
    $.ajax({
        url: '/admin/get_atributs',
        type: 'GET',
        data: { 'id': id },
        success: (data) => {
            console.log(data)
        }
    })
})



$(document).on('submit', 'form#prod_form', (e) => {
    e.preventDefault()
    let url = $(e.target).attr("action")
    let data = $(e.target).serialize()


    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: (data) => {
            console.log(data)
            window.location = '/admin/products'
        },
        error: (error) => {
            let data = error.responseJSON
            for(let key in data.product) {
                let dict_key = key
                if (key == 'name') {
                    dict_key += `#${data.lang}`
                }
                console.log(data.product[key])  
                $(`[name='${dict_key}'] + .invalid-feedback`).html(data.product[String(key)])
            }
        }
    })

})
$('#btn_lock').click(function() {
    $('.auth>p').text('')
    let code = $('#input_code').val().trim();
    $.post('/validateAuthcode', { //发送post请求
        authcode: code
    }, function (res) {
        if (res !== 'Success') {
            $('.auth>p').text(res)
        } else {
            location.href = '/index'
        }
    });
});
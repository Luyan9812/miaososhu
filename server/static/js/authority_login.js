$('#btn_lock').click(function() {
    let account = $('#account').val().trim();
    let password = $('#password').val().trim();
    if (account === '' || password === '') return;
    $.post('/loginValidate', {
        uname: account,
        upassword: password
    }, function (res) {
        if (res !== 'Success') {
            alert(res);
        } else {
            location.href = '/manager'
        }
    });
});
checkBtnSize()

$('#btn_download').click(function() {
	window.open($(this).attr('href'));
});

$('#btn_update').click(function() {
	let that = this;
	let url = $(this).attr('href');
	console.log('更新')
	$.post('/cloudSave', { //发送post请求
		url: url
	}, function (res) {
		alert('已添加到更新队列，勿重复更新');
		$(that).prop('disabled', true);
	});
});

$('#btn_read').click(function() {
	let chapter_id = $(this).attr('ch_id');
	location.href = '/chapter/' + chapter_id;
});

function checkBtnSize() {
	if ($('.op_btns').children('button').length < 3) return;
	$('.op_btns').children('button').css('width', '200px');
}
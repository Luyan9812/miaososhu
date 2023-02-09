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
		alert('已成功添加到更新队列，勿重复更新');
		$(that).prop('disabled', true);
	});
});

$('#btn_read').click(function() {
	let chapter_id = $(this).attr('ch_id');
	location.href = '/chapter/' + chapter_id;
});

$('#select_finish').change(function () {
	let status = $(this).val();
	let book_id = $(this).attr('book_id');
	$.post('/updateBookStatus', { //发送post请求
		book_id: book_id,
		finish_status: status
	}, function (res) {
		alert(res)
	});
});

function checkBtnSize() {
	if ($('.op_btns').children('button').length < 3) return;
	$('.op_btns').children('button').css('width', '200px');
}
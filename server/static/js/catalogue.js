$('#btn_download').click(function() {
	window.open($(this).attr('href'));
});

$('#btn_save').click(function() {
	console.log('save');
});

$('#btn_read').click(function() {
	let chapter_id = $(this).attr('ch_id');
	location.href = '/chapter/' + chapter_id;
});
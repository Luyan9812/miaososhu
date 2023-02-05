$('.logo').click(function () {
	location.href = 'index.html';
});

$('#input_kw').keydown(function (e) {
	if (e.keyCode != 13) return;
	$('#search_icon').click();
});

$('#search_icon').click(function () {
	let type = $('#search_type').val();
	let kw = $('#input_kw').val();
	console.log(type + kw);
});
$('.logo').click(function () {
	location.href = '/index';
});

$('#search_type').change(function () {
	let n = parseInt($(this).val());
	if (n === 1) $('#input_kw').attr('placeholder', '键入书名');
	else if (n === 2) $('#input_kw').attr('placeholder', '键入作者名');
	else $('#input_kw').attr('placeholder', '书名@作者名');
});

$('#input_kw').keydown(function (e) {
	if (e.keyCode !== 13) return;
	$('#search_icon').click();
});

$('#search_icon').click(function () {
	if (!onCheck()) return;
	$('#form_search').submit();
});

function onCheck() {
	let kw = $('#input_kw').val().trim();
	let type = parseInt($('#search_type').val());
	if (kw.length < 2) return false;
	if (type === 3) {
		let pos = kw.indexOf('@');
		if (pos <= 0 || pos >= kw.length - 1) return false;
	}
	return true;
}
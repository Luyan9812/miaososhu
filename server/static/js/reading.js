$('.btn_up').click(function() {
	let id = $(this).attr('data-id');
	if (id < 0) return;
	location.href = '/chapter/' + id;
});

$('.btn_down').click(function() {
	let id = $(this).attr('data-id');
	if (id < 0) return;
	location.href = '/chapter/' + id;
});

$('.btn_catalogue').click(function() {
	location.href = '/catalogue/' + $(this).attr('data-id');
});

function hideBtn() {
	let pre_id = parseInt($('.btn_up').attr('data-id'));
	let after_id = parseInt($('.btn_down').attr('data-id'));
	if (pre_id < 0) $('.btn_up').hide();
	if (after_id < 0) $('.btn_down').hide();
}
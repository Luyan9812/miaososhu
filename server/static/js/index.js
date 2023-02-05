$('.book_box>img').click(function () {
	let url = $(this).attr('href');
	location.href = url;
});
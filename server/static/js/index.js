$('.book_box>img').click(function () {
	let url = $(this).attr('href');
	if (url.startsWith('http'))
		window.open(url);
	else location.href = url;
});

function loadOtherNovels() {
	$.post('/others', { //发送post请求
		id: 1
	}, function (res) {
		renderOtherNovels(JSON.parse(res));
	});
}

function renderOtherNovels(novels) {
	let lineStr = '';
	let lines = Math.ceil(1.0 * novels.length / 3);
	for (let i = 0; i < lines; i++) {
		lineStr += '<div class="book_line">';
		let nitems = (i == lines - 1 ? novels.length % 3: 3);
		for (let j = 0; j < nitems; j++) {
			let book = novels[i * 3 + j];
			lineStr += '<div class="book_box">';
			lineStr += '<img href="'+ book.url +'" src="'+ book.cover_img +'"/>'
			lineStr += '<div class="box_right">'
			lineStr += '<div class="box_head">'
			lineStr += '<a href="'+ book.url +'" target="_blank">'+ book.book_name +'</a>'
			lineStr += '<p>'+ book.author_name +'</p>'
			lineStr += '<div style="clear: both;"></div>'
			lineStr += '</div>'
			lineStr += '<p>'+ book.info.substring(0, 80) + '...' +'</p>'
			lineStr += '</div>'
			lineStr += '</div>'
		}
		lineStr += '</div>';
	}
	$('.group_name>img').hide();
	$('#other_books').append($(lineStr));

	$('.book_box>img').click(function () {
		let url = $(this).attr('href');
		if (url.startsWith('http'))
			window.open(url);
		else location.href = url;
	});
	checkFontSize();
}

function checkFontSize() {
	let boxs = $('.box_head');
	for (let i = 0; i < boxs.length; i++) {
		let book_name = $(boxs[i]).find('a');
		let author_name = $(boxs[i]).find('p');
		let length = book_name.text().length + author_name.text().length;
		if (length <= 12) continue;
		book_name.css('font-size', '12px');
		author_name.css('font-size', '12px');
		if (length > 16) {
			let bt = book_name.text();
			let nl = bt.length - (length - 16);
			book_name.text(bt.substring(0, nl) + '...');
		}
	}
}
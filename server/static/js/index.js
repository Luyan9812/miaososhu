$('.book_box>img').click(function () {
	let url = $(this).attr('href');
	if (url.startsWith('http'))
		window.open(url);
	else location.href = url;
});

$('.tag').click(function () {
	$(this).hide();
	let href = $(this).find('p').attr('href');
	let type = parseInt($(this).find('p').attr('type'));
	if (type === 0) { // 下载逻辑
		window.open(href);
		return;
	} else { // 转存逻辑
		$.post('/cloudSave', { //发送post请求
			url: href
		}, function (res) {
			console.log(JSON.parse(res))
		});
	}
});

$('.page_wrapper>p').click(function () {
	let page = $(this).text().trim();
	location.href = '/local?page=' + page;
});

function loadOtherNovels() {
	$.post('/otherRecommend', { //发送post请求
		id: 1
	}, function (res) {
		$('.group_name>img').hide();
		renderOtherNovels(JSON.parse(res));
	});
}

function renderOtherNovels(novels) {
	let lineStr = '';
	let lines = Math.ceil(1.0 * novels.length / 3);
	let last_items = novels.length % 3 == 0 ? 3 : novels.length % 3;
	for (let i = 0; i < lines; i++) {
		lineStr += '<div class="book_line">';
		let nitems = (i == lines - 1 ? last_items: 3);
		for (let j = 0; j < nitems; j++) {
			let book = novels[i * 3 + j];
			let cover_path = "/static/covers/" + book.book_name + "_" + book.author_name + ".jpg";
			lineStr += '<div class="book_box">';
			lineStr += '<img href="'+ book.url +'" src="'+ cover_path +'"/>';
			lineStr += '<div class="box_right">';
			lineStr += '<div class="box_head">';
			lineStr += '<a href="'+ book.url +'" target="_blank">'+ book.book_name +'</a>';
			lineStr += '<p>'+ book.author_name +'</p>';
			lineStr += '<div style="clear: both;"></div>';
			lineStr += '</div>';
			lineStr += '<p>'+ book.info.substring(0, 80) + '...' +'</p>';
			lineStr += '<div class="tag">';
			if (book.book_type === '未知') {
				lineStr += '<p type="1" href="'+ book.url +'" class="green">转存</p>';
			} else {
				lineStr += '<p type="0" href="/static/epub/'+ book.book_name +'_'+ book.author_name +'.epub" class="blue">下载</p>';
			}
			lineStr += '</div>';
			lineStr += '</div>';
			lineStr += '</div>';
		}
		lineStr += '</div>';
	}
	$('#other_books').append($(lineStr));
	$('.book_box>img').click(function () {
		let url = $(this).attr('href');
		if (url.startsWith('http'))
			window.open(url);
		else location.href = url;
	});
	$('.tag').click(function () {
		$(this).hide();
		let href = $(this).find('p').attr('href');
		let type = parseInt($(this).find('p').attr('type'));
		if (type === 0) { // 下载逻辑
			window.open(href);
			return;
		} else { // 转存逻辑
			$.post('/cloudSave', { //发送post请求
				url: href
			}, function (res) {
				console.log(JSON.parse(res))
			});
		}
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
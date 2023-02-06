function loadOtherSearchResults() {
	let kw = $('#div_otherSearch').attr('data-kw');
	let type = parseInt($('#div_otherSearch').attr('data-type'));
	$.post('/otherSearch', { //发送post请求
		kw: kw,
		type: type
	}, function (res) {
		$('.group_name>img').hide();
		renderOtherSearchResults(JSON.parse(res));
	});
}

function renderOtherSearchResults(books) {
	if (books.length === 0) {
		$('.search_table').hide();
		$('#div_otherSearch .search_none').show();
		return;
	}
	let str = '';
	for (let i = 0; i < books.length; i++) {
		let book = books[i];
		str += '<tr>';
		str += '<td><a href="'+ book.url +'">'+ book.book_name +'</a></td>';
		str += '<td>'+ book.author_name +'</td>';
		str += '<td>'+ (book.update_time == "" ? "未知": book.update_time) +'</td>';
		str += '<td><img href="'+ book.url +'" class="img_reload" src="/static/img/reload.png"/></td>';
		str += '</tr>';
	}
	$('.search_table').append($(str));
	$('.img_reload').click(function() {
		let url = $(this).attr('href')
		$.post('/cloudSave', { //发送post请求
			url: url
		}, function (res) {
			console.log(JSON.parse(res))
		});
	});
}
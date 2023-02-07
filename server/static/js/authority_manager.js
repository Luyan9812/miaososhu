bindSaveDelete()

$('#logout').click(function() {
	location.href = '/logout';
});

$('#random_add').click(function() {
	$.post('/addAuthcode', { //发送post请求
        authcode: '$random$'
    }, function (res) {
		let obj = JSON.parse(res);
		if (obj.status !== 1) return;
		addAuthcode(obj.aid, obj.authcode, obj.valid_times)
    });
});

$('#add').click(function() {
	$('table').append(getAddStr());
	bindSaveDelete()
});

function addAuthcode(aid, authcode, validTimes) {
	let item = '<tr>';
	item += '<td>'+ authcode +'</td>';
	item += '<td><input type="text" value="'+ validTimes +'"/></td>';
	item += '<td class="td_op">';
	item += '<img data-id="'+ aid +'" class="delete" src="/static/img/delete.png"/>';
	item += '<img data-id="'+ aid +'" class="save" src="/static/img/save.png"/>';
	item += '</td>';
	item += '</tr>';
	$('table').append($(item));
	bindSaveDelete()
}

function bindSaveDelete() {
	$('.save').click(function() {
		let id = $(this).attr('data-id');
		if (id === '-1') { // 添加的逻辑

		} else { // 更新的逻辑

		}
	});

	$('.delete').click(function() {
		$(this).parent().parent().remove()
		let id = parseInt($(this).attr('data-id'));
		if (id === -1) return;
		$.post('/removeAuthcode', { //发送post请求
			aid: id
		}, function (res) {
			console.log(res)
		});
	});
}

function getAddStr() {
	let item = '<tr>';
	item += '<td><input type="text" placeholder="鉴权码"/></td>';
	item += '<td><input type="text" placeholder="次数"/></td>';
	item += '<td class="td_op">';
	item += '<img data-id="-1" class="delete" src="/static/img/delete.png"/>';
	item += '<img data-id="-1" class="save" src="/static/img/save.png"/>';
	item += '</td>';
	item += '</tr>';
	return $(item);
}
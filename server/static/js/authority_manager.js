$('#logout').click(function() {
	console.log('logout');
});

$('#random_add').click(function() {
	console.log('random add');
});

$('#add').click(function() {
	$('table').append(getAddStr());
	
	$('.save').click(function() {
		let id = $(this).attr('data-id');
		let times = $(this).parent('td').siblings().children('input').val();
		clickSave(id, times);
	});
	
	$('.delete').click(function() {
		let id = $(this).attr('data-id');
		clickDelete(id);
	});
});

$('.save').click(function() {
	let id = $(this).attr('data-id');
	let times = $(this).parent('td').siblings().children('input').val();
	clickSave(id, times);
});

$('.delete').click(function() {
	let id = $(this).attr('data-id');
	clickDelete(id);
});

function clickSave(id, times) {
	console.log(id);
	console.log(times);
}

function clickDelete(id) {
	console.log(id);
	if (id == -1) {
		$('table').find('tr:last-child').remove();
		return;
	}
}

function getAddStr() {
	let item = '<tr>';
	item += '<td><input type="text" placeholder="鉴权码"/></td>';
	item += '<td><input type="text" placeholder="次数"/></td>';
	item += '<td class="td_op">';
	item += '<img data-id="-1" class="delete" src="img/delete.png"/>';
	item += '<img data-id="-1" class="save" src="img/save.png"/>';
	item += '</td>';
	item += '</tr>';
	return $(item);
}
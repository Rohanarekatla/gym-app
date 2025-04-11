var now = new Date();

var year = now.getFullYear();
var month = (now.getMonth() + 1).toString().padStart(2, '0');
var day = now.getDate().toString().padStart(2, '0');
var hours = now.getHours().toString().padStart(2, '0');
var minutes = now.getMinutes().toString().padStart(2, '0');
var seconds = now.getSeconds().toString().padStart(2, '0');

var current_dt = year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
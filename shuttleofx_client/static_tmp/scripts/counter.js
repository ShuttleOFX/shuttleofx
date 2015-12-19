var currentUrl = window.location.href;
var decomposedUrl = currentUrl.split("?");

var skip;
var count;

var totalPlugins = $("#totalPlugins").val();

if (decomposedUrl.length < 2) {
  count = 10;
  skip = 1;
}
else {
  decomposedUrl = decomposedUrl[1].split("&");
  count = decomposedUrl[0].split("=")[1];
  skip = decomposedUrl[1].split("=")[1];
}

$('select#pageSize').val(count);

if (skip <= 1) {
    $('#previous').addClass('disabled');
}
else if (skip == Math.ceil(totalPlugins/count)) {
  $('#next').addClass('disabled');
}

$('select#pageSize').change(function(){
  count = $('select#pageSize').val();
  if (skip > Math.ceil(totalPlugins/$('select#pageSize').val())) {
    skip = Math.ceil(totalPlugins/$('select#pageSize').val());
  }
  window.location.href = "/plugin?count=" + count + "&skip=" + skip;
});

$('#next a').click(function(event){
  event.preventDefault();
  if (!$("#next").hasClass("disabled")) {
    skip ++;
    window.location.href = "/plugin?count=" + count + "&skip=" + skip;
  }
});

$('#previous a').click(function(event){
  event.preventDefault();
  if (!$("#previous").hasClass("disabled")) {
    skip --;
    window.location.href = "/plugin?count=" + count + "&skip=" + skip;
  }
});

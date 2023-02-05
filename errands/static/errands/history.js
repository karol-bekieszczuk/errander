$(document).ready(function(){
  $('#mapDisplayBtn').click(function(){
    if ($('#displayTable').is(':hidden')){
        $('#displayTable').css('display', 'block');
    } else {
        $('#displayTable').css('display', 'none');
    }
  });
});
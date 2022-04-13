$('.hidden-on-default').css('display','none'); // Hide the text input box in default

function showInputField(idCheck, idField) {
   if($('#'+idCheck).prop('checked')) {
         $('#'+idField).css('display','block');
       } else {
         $('#'+idField).css('display','none');
       }
}

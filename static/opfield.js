$('.op-hidden-on-default').css('display','none'); // Hide the text input box in default

function showOPField(idCheck, idField1, idField2) {
   if($('#'+idCheck).prop('checked')) {
         $('#'+idField1).css('display','block');
         $('#'+idField2).css('display','block');
       } else {
         $('#'+idField1).css('display','none');
         $('#'+idField2).css('display','none');
       }
}

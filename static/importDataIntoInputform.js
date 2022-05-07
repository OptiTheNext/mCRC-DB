function importData() {
    var pid = $('#pat_id_import').val();
    $.getJSON("/api/getDataForID", "pat_id_import="+pid, function(result){
        console.log(result);
        $.each(result, function(key, value) {
            if($('#'+key).prop("type") == "checkbox") {
                console.log("Checkbox!");
                console.log(key);
                console.log(value);
                $('#'+key).prop('checked', Boolean(value)).trigger("change");
            } else {
                $('#'+key).val(value);
                console.log(key);
                console.log(value);
            }
        })
    })
}

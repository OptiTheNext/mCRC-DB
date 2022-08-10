function importData() {
    var pid = $('#pat_id_import').val();
    $.getJSON("/api/getDataForID", "pat_id_import="+pid, function(result){
        console.log(result);
        $.each(result, function(key, value) {
            // Check if specific subfields of default-hidden spans have input
            if(key === "previous_surgery_date")
            {
                $("#PreviousOPs").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "pve_date")
            {
                $("#PVECheck").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "second_surgery_planned")
            {
                $("#secondOP_Check").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "third_surgery_planned")
            {
                $("#thirdOP_Check").prop('checked', Boolean(value)).trigger("change");
            }

            if(key === "diagnosis2") {
                $("#diagnose2_check").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "pve_date") {
                $("#pve_check").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "op_date_Surgery2") {
                $("#secondOP_check").prop('checked', Boolean(value)).trigger("change");
            }
            if(key === "op_date_Surgery3") {
                $("#thirdOP_check").prop('checked', Boolean(value)).trigger("change");
            }

            if($('#'+key).prop("type") == "checkbox") {
                $('#'+key).prop('checked', Boolean(value)).trigger("change");
            } else {
                $('#'+key).val(value);
            }
        })
    })
}

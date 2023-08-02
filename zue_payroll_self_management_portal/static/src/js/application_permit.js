'use strict';

odoo.define('zue_payroll_self_management_portal.javascript',function(require){

    require('web.dom_ready');

    $("#permit_days").prop('readonly', true);
    
    var severalDays = $('#severalDays');
    var saveData = $('#SaveData');
    
    var _validate_permit_days = function(e){
        if (severalDays.prop('checked')){
            $("#permit_days").prop('readonly', false);
            $("#initial_hour").prop('readonly', true);
            $("#final_hour").prop('readonly', true);
        }else {
            $("#permit_days").prop('readonly', true);
            $("#initial_hour").prop('readonly', false);
            $("#final_hour").prop('readonly', false);
            $("#initial_hour").removeClass('is-invalid')
            $("#final_hour").removeClass('is-invalid')
        }
    }

    var _save_data = function(e){

        let initial_hour = $("#initial_hour").val();
        let final_hour = $("#final_hour").val();
        let permit_date = $("#permit_date").val();        
        let resp = true;

        //valid fields
        $("#permit_date").val() == '' ? ($("#permit_date").addClass('is-invalid'), resp = false) : ($("#permit_date").removeClass('is-invalid')) ;
        
        if (severalDays.prop('checked')){
            $("#permit_days").val() == '' || $("#permit_days").val() == 0 ? ($("#permit_days").addClass('is-invalid'), resp = false) : ($("#permit_days").removeClass('is-invalid')) ;
            $("#initial_hour").val();

            $("#initial_date").val(permit_date);
            $("#final_date").val(permit_date);
        }else{

            initial_hour == '' ? ($("#initial_hour").addClass('is-invalid'), resp = false) : ($("#initial_hour").removeClass('is-invalid')) ;
            final_hour == '' ? ($("#final_hour").addClass('is-invalid'), resp = false) : ($("#final_hour").removeClass('is-invalid')) ;

            let initial_date = permit_date + ' ' + initial_hour + ':00' ;
            let final_date = permit_date + ' ' + final_hour + ':00';

            $("#initial_date").val(initial_date);
            $("#final_date").val(final_date);
            $("#permit_days").val(0);
        }

        return resp;
    }
    
    severalDays.click(_validate_permit_days);
    saveData.click(_save_data);

});
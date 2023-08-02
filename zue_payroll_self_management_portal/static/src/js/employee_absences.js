//Funcionamiento fecha final
$(function () {
    $(document).on("blur", ".txt_number_of_days", function () {
        var value_txt_number_of_days = parseInt(document.getElementById("number_of_days").value);
        var value_date_start = new Date(document.getElementById("date_start").value);
        value_date_start.setDate(value_date_start.getDate() + value_txt_number_of_days);
        var year_end = value_date_start.getFullYear().toString();
        var month_end = (value_date_start.getMonth()+1).toString();
        var day_end = value_date_start.getDate().toString();
        if (month_end.length == 1){
            month_end = "0"+month_end
        }
        if (day_end.length == 1){
            day_end = "0"+day_end
        }
        var date_end = year_end+"-"+month_end+"-"+day_end;
        document.getElementById('date_end').value = date_end;
    });
});
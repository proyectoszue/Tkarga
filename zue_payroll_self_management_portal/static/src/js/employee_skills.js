//Funcionamiento modal añadir habilidad
$(function () {
    $(document).on("blur", ".skill_type_select", function () {
        var skill_type_select = document.getElementById("field_skill_type_id");
        var skill_type_select_id = skill_type_select.value;
        var select_filter_skill = document.getElementById("field_skill_id");
        for (var i = 1; i < select_filter_skill.options.length; i++) {
            if (skill_type_select_id == select_filter_skill[i].getAttribute('skill-type-id')){
                select_filter_skill[i].hidden = false;
            } else{
                select_filter_skill[i].hidden = true;
            }
        }
        var select_filter_level_skill = document.getElementById("field_skill_level_id");
        for (var i = 1; i < select_filter_level_skill.options.length; i++) {
            if (skill_type_select_id == select_filter_level_skill[i].getAttribute('skill-type-id')){
                select_filter_level_skill[i].hidden = false;
            } else{
                select_filter_level_skill[i].hidden = true;
            }
        }
    });
    $(document).on("blur", ".skill_select", function () {
        var selected_skill = document.getElementById("field_skill_id").value;
        var select_filter_skill = document.getElementById("field_skill_id");
        for (var i = 1; i < select_filter_skill.options.length; i++) {
            if (selected_skill == select_filter_skill[i].value && "True" == select_filter_skill[i].getAttribute('is_other')){
                document.getElementById("field_skill_other").hidden = false;
            } else{
                document.getElementById("field_skill_other").hidden = true;
            }
        }
    });

});

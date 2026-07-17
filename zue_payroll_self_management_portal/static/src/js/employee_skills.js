//Funcionamiento modal añadir habilidad
$(function () {
    // Función para filtrar opciones por skill-type-id
    function filterOptionsBySkillType(selectId, skillTypeId) {
        var selectElement = document.getElementById(selectId);
        if (!selectElement) return;

        for (var i = 1; i < selectElement.options.length; i++) {
            var option = selectElement.options[i];
            if (skillTypeId == option.getAttribute('skill-type-id')) {
                option.style.display = 'block';
                option.disabled = false;
            } else {
                option.style.display = 'none';
                option.disabled = true;
            }
        }
        // Resetear el valor seleccionado
        selectElement.selectedIndex = 0;
    }

    // Evento change para el selector de tipo de habilidad
    $(document).on("change", "#field_skill_type_id", function () {
        var skillTypeId = $(this).val();

        if (skillTypeId) {
            // Filtrar habilidades
            filterOptionsBySkillType("field_skill_id", skillTypeId);

            // Filtrar niveles de habilidad
            filterOptionsBySkillType("field_skill_level_id", skillTypeId);

            // Ocultar el campo "other" al cambiar tipo
            $("#field_skill_other").hide().val('');
        }
    });

    // Evento change para el selector de habilidad
    $(document).on("change", "#field_skill_id", function () {
        var selectedSkill = $(this).val();
        var selectedOption = $(this).find('option:selected');

        if (selectedSkill && selectedOption.attr('is_other') === 'True') {
            $("#field_skill_other").show().prop('required', true);
        } else {
            $("#field_skill_other").hide().prop('required', false).val('');
        }
    });

    // Resetear formulario cuando se cierre el modal
    $('#modalSkill').on('hidden.bs.modal', function () {
        $(this).find('form')[0].reset();
        $("#field_skill_other").hide().prop('required', false);

        // Mostrar todas las opciones nuevamente
        $("#field_skill_id option, #field_skill_level_id option").each(function() {
            $(this).show().prop('disabled', false);
        });
    });

    // Inicializar el estado del formulario cuando se abra el modal
    $('#modalSkill').on('shown.bs.modal', function () {
        $("#field_skill_other").hide();
        // Asegurar que todos los selects estén en su estado inicial
        $("#field_skill_type_id, #field_skill_id, #field_skill_level_id").val('');

        // Mostrar todas las opciones
        $("#field_skill_id option, #field_skill_level_id option").each(function() {
            $(this).show().prop('disabled', false);
        });
    });
});
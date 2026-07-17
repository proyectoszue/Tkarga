//Funcionamiento fecha final y validaciones
$(function () {
    // Función para formatear fecha a string YYYY-MM-DD
    function formatDateToString(date) {
        var year = date.getFullYear().toString();
        var month = (date.getMonth() + 1).toString().padStart(2, '0');
        var day = date.getDate().toString().padStart(2, '0');
        return year + "-" + month + "-" + day;
    }

    // Función auxiliar para parsear localmente "YYYY-MM-DD"
    // Esto evita problemas de zona horaria que ocurren con new Date("YYYY-MM-DD")
    function parseLocalDate(dateString) {
        if (!dateString) return null;
        var parts = dateString.split('-');
        // new Date(year, monthIndex, day) crea la fecha en hora local
        return new Date(parts[0], parts[1] - 1, parts[2]);
    }

    // Función para calcular fecha final
    function calculateEndDate() {
        var numberOfDays = parseInt($("#number_of_days").val()) || 0;
        var startDateValue = $("#date_start").val();

        if (!startDateValue || numberOfDays <= 0) {
            $("#date_end").val('');
            return;
        }

        var startDate = parseLocalDate(startDateValue);

        // Verificar que la fecha de inicio sea válida
        if (!startDate || isNaN(startDate.getTime())) {
            $("#date_end").val('');
            return;
        }

        // Calcular fecha final
        // Si pides 1 día, fecha fin = fecha inicio.
        // Si pides 2 días, fecha fin = fecha inicio + 1 día.
        // Fórmula general: fecha inicio + (días - 1)
        var endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + (numberOfDays - 1));

        // Formatear y establecer la fecha final
        var formattedEndDate = formatDateToString(endDate);
        $("#date_end").val(formattedEndDate);
    }

    // Evento input para recalcular en tiempo real
    $(document).on("input", "#number_of_days", function () {
        calculateEndDate();
    });

    // Evento change para cuando se cambia la fecha de inicio
    $(document).on("change", "#date_start", function () {
        calculateEndDate();
    });

    // Validación adicional: evitar números negativos o inválidos
    $(document).on("input", "#number_of_days", function () {
        var value = parseInt($(this).val());
        // Si no es número o es menor a 1, corregir (aunque el input=number ayuda, prevenir manual)
        if (isNaN(value) || value < 1) {
            // Permitir que el usuario borre y escriba, pero al salir o finalizar, validar.
            // Aqui solo prevenimos negativos directos si fuera necesario, 
            // pero mejor dejamos que calculateEndDate maneje el logic 
            // y solo forzamos limites si es critico.
            // $(this).val(1); 
        }

        // Opcional: limitar a un máximo razonable si se requiere
        if (value > 365) {
            $(this).val(365);
        }
    });

    // Validación de fecha de inicio: no permitir fechas pasadas
    $(document).on("change", "#date_start", function () {
        var startDateValue = $(this).val();
        if (!startDateValue) return;

        var selectedDate = parseLocalDate(startDateValue);
        var today = new Date();
        today.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fechas

        if (selectedDate < today) {
            // Opcional: mostrar advertencia o limpiar
            // alert("La fecha de inicio no puede ser anterior a hoy");
            // $(this).val('');
            // $("#date_end").val('');
        }
    });

    // Inicialización: calcular fecha final si ya hay valores
    $(document).ready(function () {
        // Establecer fecha mínima como hoy
        var today = new Date();
        $("#date_start").attr('min', formatDateToString(today));

        // Calcular fecha final si ya hay valores preestablecidos
        if ($("#date_start").val() && $("#number_of_days").val()) {
            calculateEndDate();
        }
    });

    // Validación antes del envío del formulario
    $(".form-application-permit").on("submit", function (e) {
        var startDate = $("#date_start").val();
        var numberOfDays = parseInt($("#number_of_days").val());
        var leaveType = $("#holiday_status_id").val();
        var description = $("#observation").val().trim();

        // Validaciones básicas
        if (!leaveType) {
            e.preventDefault();
            Swal.fire({ icon: 'error', title: 'Error', text: 'Por favor seleccione un tipo de ausencia' });
            return false;
        }

        if (!startDate) {
            e.preventDefault();
            Swal.fire({ icon: 'error', title: 'Error', text: 'Por favor seleccione una fecha de inicio' });
            return false;
        }

        if (!numberOfDays || numberOfDays <= 0) {
            e.preventDefault();
            Swal.fire({ icon: 'error', title: 'Error', text: 'Por favor ingrese un número válido de días' });
            return false;
        }

        if (!description) {
            e.preventDefault();
            Swal.fire({ icon: 'error', title: 'Error', text: 'Por favor ingrese una descripción' });
            return false;
        }

        return true;
    });
});

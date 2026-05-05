//Funcionamiento filtro de documentos expirados
$(function () {
    // Función para filtrar elementos por atributo expired
    function filterDocumentsByExpired(containerId, showOnlyExpired) {
        var container = document.getElementById(containerId);
        if (!container) return;

        for (var i = 0; i < container.children.length; i++) {
            var element = container.children[i];
            var isExpired = element.getAttribute('expired') === 'True';

            if (showOnlyExpired) {
                // Mostrar solo documentos expirados
                if (isExpired) {
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
            } else {
                // Mostrar todos los documentos
                element.style.display = 'block';
            }
        }
    }

    // Evento change para el checkbox de filtro
    $(document).on("change", "#chk_filter_expired", function () {
        var showOnlyExpired = $(this).is(':checked');

        // Filtrar vista Kanban
        filterDocumentsByExpired("div_view_kanban", showOnlyExpired);

        // Filtrar vista Lista
        var tableBody = document.getElementById("table_view_list");
        if (tableBody) {
            for (var i = 0; i < tableBody.children.length; i++) {
                var row = tableBody.children[i];
                var isExpired = row.getAttribute('expired') === 'True';

                if (showOnlyExpired) {
                    // Mostrar solo filas de documentos expirados
                    if (isExpired) {
                        row.style.display = 'table-row';
                    } else {
                        row.style.display = 'none';
                    }
                } else {
                    // Mostrar todas las filas
                    row.style.display = 'table-row';
                }
            }
        }
    });

    function updateDocumentCount() {
        var kanbanContainer = document.getElementById("div_view_kanban");
        var tableContainer = document.getElementById("table_view_list");
        var visibleKanban = 0;
        var visibleTable = 0;

        if (kanbanContainer) {
            for (var i = 0; i < kanbanContainer.children.length; i++) {
                if (kanbanContainer.children[i].style.display !== 'none') {
                    visibleKanban++;
                }
            }
        }

        if (tableContainer) {
            for (var i = 0; i < tableContainer.children.length; i++) {
                if (tableContainer.children[i].style.display !== 'none') {
                    visibleTable++;
                }
            }
        }

    }

    $(document).ready(function() {
        $("#chk_filter_expired").prop('checked', false);
        filterDocumentsByExpired("div_view_kanban", false);

        var tableBody = document.getElementById("table_view_list");
        if (tableBody) {
            for (var i = 0; i < tableBody.children.length; i++) {
                tableBody.children[i].style.display = 'table-row';
            }
        }
    });
});
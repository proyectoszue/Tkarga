//Funcionamiento filtro de documentos expirados
$(function () {
    $(document).on("click", ".filter_expired", function () {
        var value_chk_filter_expired = document.getElementById("chk_filter_expired").checked;
        var div_view_kanban = document.getElementById("div_view_kanban");
        for (var i = 0; i < div_view_kanban.children.length; i++) {
            if (value_chk_filter_expired == true){
                if ("True" == div_view_kanban.children[i].getAttribute('expired')){
                    div_view_kanban.children[i].hidden = false;
                } else{
                    div_view_kanban.children[i].hidden = true;
                }
            } else{
                div_view_kanban.children[i].hidden = false;
            }
        }
        var table_view_list = document.getElementById("table_view_list");
        for (var i = 0; i < table_view_list.children.length; i++) {
            if (value_chk_filter_expired == true){
                if ("True" == table_view_list.children[i].getAttribute('expired')){
                    table_view_list.children[i].hidden = false;
                } else{
                    table_view_list.children[i].hidden = true;
                }
            }else{
                table_view_list.children[i].hidden = false;
            }
        }
    });
});
//https://gijgo.com/tree/configuration/dataSource - откуда взято дерево
// https://www.daterangepicker.com/#options - datepicker

// import * as treex from..TreeX
// document.addEventListener("DOMContentLoaded", action_after_load_page);
let tree_object;
let select2_clietn;

function settings_collect() {
    map_settings = {};

    period_item = document.querySelector("[name='period']");
    if ((period_item != null) && (period_item.value != '')) {
        dates = period_item.value.split("-");
        map_settings["date_start"] = dates[0].replaceAll("/", ".").trim();
        map_settings["date_stop"] = dates[1].replaceAll("/", ".").trim();
    }
    client_item = document.querySelector("[name='client']");
    if ((client_item != null) && (client_item.value != '')) {
        map_settings["client_id"] = client_item.value;
    }

    task_name_item = document.querySelector("[name='task_name']");
    if ((task_name_item != null) && (task_name_item.value != '')) {
        map_settings["task_name"] = task_name_item.value;
    }

    only_wichout_account = document.querySelector("[name='only_wichout_account']");
    if ((only_wichout_account != null) && (only_wichout_account.checked)) {
        map_settings["only_wichout_account"] = "true";
    }
    return map_settings
}

function tree_load_data_to_tree(data) {
    // [{ text: 'foo', id: "root", checked: true, children: [{ text: 'bar', id: "child" }] }]
    data_source = []
    for (client of data.array_of_client) {
        children = []
        client_id = ""
        for (task of data.dic_of_task[client]) {
            children.push({
                text: "" + task["task_name"] + " потрачено (" +
                    seconds_to_hh_mm(task["duration"]) + " ч. м.)",
                id: "t_" + task["task_id"]
            });
            client_id = task["client_id"];
        }
        dic_data_of_client = { text: client, checked: true, id: "c_" + client_id, children: children }
        data_source.push(dic_data_of_client)
    }
    // tree_object.dataSource = data_source;
    tree_object.render(data_source);
    tree_object.expandAll();
}

function tree_recreate() {
    $.ajax({
        type: "get",
        url: "/api/reports/time_track/",
        data: settings_collect(),
        headers: {
            "Content-Type": "application/json",
            // "X-Requested-With": "XMLHttpRequest",
            // "X-CSRFToken": getCookie("csrftoken"), // don't forget to include the 'getCookie' function
        },
        success: (data) => {
            tree_load_data_to_tree(data);
        },
        error: (error) => {
            console.log(error);
        }
    });
}

function settings_clearAll() {
    period_item = document.querySelector("[name='period']");
    if ((period_item != null) && (period_item.value != '')) {
        period_item.value = "";
    }
    client_item = document.querySelector("[name='client']");
    if ((client_item != null) && (client_item.value != '')) {
        // $('#client').val(null).trigger('change');
        select2_clietn.val(null).trigger('change');
    }

    task_name_item = document.querySelector("[name='task_name']");
    if ((task_name_item != null) && (task_name_item.value != '')) {
        task_name_item.value = "";
    }

    only_wichout_account = document.querySelector("[name='only_wichout_account']");
    if ((only_wichout_account != null) && (!only_wichout_account.checked)) {
        only_wichout_account.checked = true;
    }

}

$(document).ready(function() {
    tree_object = $('#tree').tree({
        primaryKey: 'id',
        uiLibrary: 'bootstrap4',
        // dataSource: [{ text: 'foo', id: "root", checked: true, children: [{ text: 'bar', id: "child" }] }],
        // dataSource: data_source,
        checkboxes: true,
        autoLoad: false
    });

    // сам отчет
    $('#btnFilter').on('click', function() {
        tree_recreate();
    });
    $('#btnCancelFilter').on('click', function() {
        settings_clearAll();
    });
    $('#btnExpandAll').on('click', function() {
        tree_object.expandAll();
    });
    $('#btnCollapsAll').on('click', function() {
        tree_object.collapseAll();
    });
    $('#btnCheckAll').on('click', function() {
        tree_object.checkAll();
    });
    $('#btnUncheckAll').on('click', function() {
        tree_object.uncheckAll();
    });
    // период формирования
    $('input[name="period"]').daterangepicker({
        opens: 'left',
        showDropdowns: true,
        locale: {
            cancelLabel: 'Отмена',
            applyLabel: 'Применить'
        }
    });
    $('input[name="period"]').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    });
    // выбор килентов
    select2_clietn = $('.js-data-client-ajax').select2({
        placeholder: '-- выберите клиента --',
        allowClear: true,
        minimumInputLength: 0,
        ajax: {
            url: '/api/clients/',
            dataType: 'json'
                // Additional AJAX parameters go here; see the end of this chapter for the full code of this example
        },
        cache: true
    });
});
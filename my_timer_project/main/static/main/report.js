//https://gijgo.com/tree/configuration/dataSource - откуда взято дерево
// https://www.daterangepicker.com/#options - datepicker

// import * as treex from..TreeX
// document.addEventListener("DOMContentLoaded", action_after_load_page);
let tree_object;
let select2_clietn;
let dcit_convert_id_to_parent;
let dict_convert_client_id_to_name;

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
    } else {
        map_settings["only_wichout_account"] = "false";
    }
    return map_settings
}

function tree_load_data_to_tree(data) {
    // [{ text: 'foo', id: "root", checked: true, children: [{ text: 'bar', id: "child" }] }]
    data_source = []
    dcit_convert_id_to_parent = {}
    dict_convert_client_id_to_name = {}
    for (client of data.array_of_client) {
        children = []
        client_id = ""
        duration_client = 0
        for (task of data.dic_of_task[client]) {
            children.push({
                text: "" + task["task_name"] + " потрачено (" +
                    seconds_to_hh_mm(task["duration"]) + " ч. м.)",
                id: "t_" + task["task_id"]
            });
            client_id = task["client_id"];
            dcit_convert_id_to_parent["t_" + task["task_id"]] = "c_" + client_id;
            duration_client = duration_client + task["duration"]
        }
        dict_convert_client_id_to_name["c_" + client_id] = client;
        client_text = client + " потрачено (" + seconds_to_hh_mm(duration_client) + " ч. м.)"
        dic_data_of_client = { text: client_text, checked: true, id: "c_" + client_id, children: children }
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

// WORK WICH REPORT SAVE PDF
function report_service_get_check_tasks() {
    let dic_client_tasks = {};
    let array_check_node = tree_object.getCheckedNodes();
    for (let node of array_check_node) {
        if (node.startsWith("t_")) {
            let parent_id = dcit_convert_id_to_parent[node];
            if (parent_id) {
                if (!(parent_id in dic_client_tasks)) {
                    dic_client_tasks[parent_id] = []
                }
                dic_client_tasks[parent_id].push(node.substring(2))
            }
        }
    }
    return dic_client_tasks;
}

function report_service_get_file_pdf(settings, file_name) {
    $.ajax({
        type: "GET",
        // dataType: 'native',
        url: "/api/reports/pdf_report/",
        headers: {
            "Content-Type": "application/json",
        },
        xhrFields: {
            responseType: 'blob'
        },
        data: settings,
        cache: false,
        traditional: true,
        success: function(blob) {
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = file_name;
            link.click();
        }
    });
}

function report_service_set_date_account(settings) {
    $.ajax({
        type: "GET",
        // dataType: 'native',
        url: "/api/reports/set_date_account/",
        headers: {
            "Content-Type": "application/json",
        },
        xhrFields: {
            responseType: 'text'
        },
        data: settings,
        cache: false,
        traditional: true,
        success: function(text) {
            let a = 4;
            window.location.href = text;
            // var link = document.createElement('a');
            // link.href = window.URL.createObjectURL(blob);
            // link.download = file_name;
            // link.click();
        }
    });
}


function report_service_get_file_name_for_client(client_id, date_start, date_stop) {
    let client_name = dict_convert_client_id_to_name[client_id];
    let date_start_str = date_start.slice(6, 10) + "_" + date_start.slice(3, 5) + "_" + date_start.slice(0, 2)
    let date_stop_str = date_stop.slice(6, 10) + "_" + date_stop.slice(3, 5) + "_" + date_stop.slice(0, 2)
    let file_name = "report_" + client_name.replaceAll(" ", "_") + "_from_" + date_start_str + "_to_" + date_stop_str + ".pdf"
    return file_name
}



function report_save_pdf() {
    let dic_of_settings_temp = settings_collect();
    let dic_of_settings = {}
    dic_of_settings["date_start"] = dic_of_settings_temp["date_start"];
    dic_of_settings["date_stop"] = dic_of_settings_temp["date_stop"];
    dic_of_settings["task_id_array"] = [];
    dic_of_settings["only_wichout_account"] = dic_of_settings_temp["only_wichout_account"];
    dic_of_settings["set_date_account"] = "true";
    let dic_client_tasks = report_service_get_check_tasks();
    for (let client_id of Object.keys(dic_client_tasks)) {
        // let dict = {}
        // let arr = dic_client_tasks[client_id]
        // arr.forEach((el, index) => dict[arr.length - index] = el);
        dic_of_settings["task_id_array_str"] = dic_client_tasks[client_id] + ","; // convert to str, else not working
        report_service_get_file_pdf(dic_of_settings,
            report_service_get_file_name_for_client(client_id, dic_of_settings["date_start"], dic_of_settings["date_stop"]));
    }
}

// function report_set_date_account() {
//     let dic_of_settings_temp = settings_collect();
//     let dic_of_settings = {}
//     dic_of_settings["date_start"] = dic_of_settings_temp["date_start"];
//     dic_of_settings["date_stop"] = dic_of_settings_temp["date_stop"];
//     dic_of_settings["task_id_array"] = [];
//     dic_of_settings["only_wichout_account"] = dic_of_settings_temp["only_wichout_account"];
//     dic_of_settings["set_date_account"] = "true";
//     dic_of_settings["client_id"] = dic_of_settings_temp["client_id"];
//     dic_of_settings["task_name"] = dic_of_settings_temp["task_name"];
//     let dic_client_tasks = report_service_get_check_tasks();
//     for (let client_id of Object.keys(dic_client_tasks)) {
//         // let dict = {}
//         // let arr = dic_client_tasks[client_id]
//         // arr.forEach((el, index) => dict[arr.length - index] = el);
//         dic_of_settings["task_id_array_str"] = dic_client_tasks[client_id] + ","; // convert to str, else not working
//         report_service_get_file_pdf(dic_of_settings,
//             report_service_get_file_name_for_client(client_id, dic_of_settings["date_start"], dic_of_settings["date_stop"]));
//     }
// }

function mark_as_account() {
    let dic_of_settings_temp = settings_collect();
    let dic_of_settings = {}
    dic_of_settings["date_start"] = dic_of_settings_temp["date_start"];
    dic_of_settings["date_stop"] = dic_of_settings_temp["date_stop"];
    dic_of_settings["task_id_array"] = [];
    dic_of_settings["only_wichout_account"] = dic_of_settings_temp["only_wichout_account"];
    dic_of_settings["set_date_account"] = "true";
    dic_of_settings["client_id"] = dic_of_settings_temp["client_id"];
    dic_of_settings["task_name"] = dic_of_settings_temp["task_name"];
    dic_of_settings["redirect"] = "true";
    let dic_client_tasks = report_service_get_check_tasks();
    for (let client_id of Object.keys(dic_client_tasks)) {
        // let dict = {}
        // let arr = dic_client_tasks[client_id]
        // arr.forEach((el, index) => dict[arr.length - index] = el);
        dic_of_settings["task_id_array_str"] = dic_client_tasks[client_id] + ","; // convert to str, else not working
        report_service_set_date_account(dic_of_settings);
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
    $('#btnSavePDF').on('click', function() {
        report_save_pdf();
    });
    $('#btnSetDateAccount').on('click', function() {
        mark_as_account();
    });


    // период формирования
    $('input[name="period"]').daterangepicker({
        opens: 'left',
        showDropdowns: true,
        startDate: moment().startOf('month'),
        endDate: moment().endOf('month'),
        ranges: {
            'Сегодня': [moment(), moment()],
            'Текущий месяц': [moment().startOf('month'), moment().endOf('month')],
            'Предыдущий месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
            'Год с текущей даты': [moment().subtract(12, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        alwaysShowCalendars: true,
        locale: {
            cancelLabel: 'Отмена',
            applyLabel: 'Применить',
            format: 'DD.MM.YYYY',
        }
    });
    // $('input[name="period"]').on('apply.daterangepicker', function(ev, picker) {
    //     $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    // });
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
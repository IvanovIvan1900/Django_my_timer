let updatable_list;

function get_info_form_page() {
    if (updatable_list == undefined) {
        updatable_list = new Array();
        let table_active_task = document.getElementById('table_active_task');
        if (table_active_task) {
            let td_task = table_active_task.querySelectorAll('td[id^="date_start_id_"]');
            for (let td of td_task) {
                map_info = new Map();
                map_info.set('td', td);
                map_info.set('date_start', new Date(td.querySelector('input').value.replace('_', 'T')));
                updatable_list.push(map_info);
            }
            if (updatable_list.length > 0) {
                // a = 4;
                let timerId = setInterval(update_duration, 60 * 1000);
                update_duration();
            }
        }
    }
}

function update_duration() {
    if (updatable_list != undefined) {
        for (let elem of updatable_list) {
            let td = elem.get('td');
            let date_start = elem.get('date_start');
            let date_now = new Date();
            let time_delta_in_sec = (date_now - date_start) / 1000;
            td.innerText = seconds_to_hh_mm(time_delta_in_sec);
        }
    }
}

// function get_present_time_delta(time_delta_in_sec) {
//     let hour_del = 3600;
//     let min_del = 60;
//     let sec = time_delta_in_sec;
//     let hours = Math.floor(sec / hour_del);
//     sec = sec % hour_del;
//     let min = Math.floor(sec / min_del);
//     let hours_str = ("0" + hours).slice(-2);
//     let min_str = ("0" + min).slice(-2);
//     let str_repr = `${hours_str}:${min_str}`;
//     return str_repr;
// }

if (updatable_list == undefined) {
    document.addEventListener("DOMContentLoaded", get_info_form_page);
}
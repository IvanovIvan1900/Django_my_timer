let info_from_page = new Map();
let has_a_table = false;
let table_time_tracker = undefined;

document.addEventListener("DOMContentLoaded", action_after_load_page);

function action_after_load_page() {
    table_time_tracker = document.getElementById('time_track_list');
    info_from_page.set('curr_string_info', undefined)
    if (table_time_tracker != undefined) {
        has_a_table = true;
        table_time_tracker.addEventListener('click', click_to_table);
    }
}

function click_to_table(event) {
    if (event.target.parentNode.dataset.date_start != undefined) {
        if (info_from_page.get('curr_string_info') != undefined) {
            close_element_to_edit();
        }
        add_element_to_edit(event.target.parentNode);
    }
}

function add_element_to_edit(td) {
    let new_info_map = new Map();

    new_info_map.set('root_td', td);
    new_info_map.set('date_start', new Date(td.dataset.date_start.replace('_', 'T')));
    new_info_map.set('date_stop', new Date(td.dataset.date_stop.replace('_', 'T')));
    new_info_map.set('duration', Number(td.dataset.duration));
    new_info_map.set('div_edit', td.querySelector('div[id="duration_edit"]'));
    new_info_map.set('date_formatter', new Intl.DateTimeFormat('ru-RU', { hour: '2-digit', minute: '2-digit' }));
    // td.innerText = "";
    let div_edit = new_info_map.get('div_edit');
    div_edit.innerHTML = ` <div class="my_inline">
    <input type="time" id="time_start" name="appt" min="00:00" max="23:59" required ">-
    <input type="time" id="time_stop" name="appt" min="00:00" max="23:59" required> = 
    <input type="time" id="time_duration" name="appt"min="00:00" max="23:59" required> </div>
        <div class="container text-center button_container" >
            <a id="accept" href="#" class="btn btn-outline-warning btn-circle " role="button" onclick="click_to_button(this);" ><img src="` + ico_checked + `"
                      class="ico-button" alt="Сохранить изменения"> </a> 
            <a id="cancel" href="#" class="btn btn-outline-warning btn-circle " role="button" onclick="click_to_button(this);"><img src="` + ico_deactive + `"
                        class="ico-button" alt="Отменить изменения"></a>   </div>`
        // изменим ширину колонок, чтобы все входило
        // let th_list = table_time_tracker.querySelectorAll('th[data-name*="width_"]');
        // for (let th of th_list) {
        //     if (th.classList.contains("width_min")) {
        //         th.style.cssText = "width: 15%"
        //     }
        //     if (th.classList.contains("width_max")) {
        //         th.style.cssText = "width: 10%"
        //     }
        // }

    new_info_map.set('time_start', div_edit.querySelector('input[id="time_start"]'));
    new_info_map.set('time_stop', div_edit.querySelector('input[id="time_stop"]'));
    new_info_map.set('time_duration', div_edit.querySelector('input[id="time_duration"]'));
    new_info_map.set('href_time_duration', td.querySelector('a[id="a_time_duration"]'));

    new_info_map.get('time_start').onblur = change_part_of_time;
    new_info_map.get('time_stop').onblur = change_part_of_time;
    new_info_map.get('time_duration').onblur = change_part_of_time;

    new_info_map.get('href_time_duration').innerText = "";
    info_from_page.set('curr_string_info', new_info_map);

    refresh_data_in_input();
}

function close_element_to_edit() {
    let info_map = info_from_page.get('curr_string_info');
    info_map.get('href_time_duration').innerText = seconds_to_hh_mm(info_map.get('duration'));
    info_map.get('div_edit').innerHTML = "";
    info_from_page.set('curr_string_info', undefined);
}

function change_part_of_time(event) {
    let id = event.currentTarget.id;
    let info_map = info_from_page.get('curr_string_info');
    let part_time = event.currentTarget.value.split(':');
    switch (id) {
        case "time_start":
            info_map.get('date_start').setHours(Number(part_time[0]), Number(part_time[1]));
            break;
        case "time_stop":
            info_map.get('date_stop').setHours(Number(part_time[0]), Number(part_time[1]));
            break;
        case "time_duration":
            // info_map.get('date_stop').setHours(info_map.get('date_start').getHours() + Number(part_time[0]), info_map.get('date_start').getMinutes() + Number(part_time[1]));
            info_map.get('date_stop').setTime(info_map.get('date_start').getTime() + (Number(part_time[0]) * 3600 + Number(part_time[1]) * 60) * 1000);
            break;

    }
    recalculate_duration();
    if (id == "time_duration") {
        refresh_data_in_input();
    }
}

function recalculate_duration() {
    let info_map = info_from_page.get('curr_string_info');
    let duration_in_sec = (info_map.get('date_stop') - info_map.get('date_start')) / 1000;
    info_map.set('duration', duration_in_sec);
    info_map.get('time_duration').value = seconds_to_hh_mm(duration_in_sec);
}

function refresh_data_in_input() {
    let info_map = info_from_page.get('curr_string_info');
    info_map.get('time_start').value = info_map.get('date_formatter').format(info_map.get('date_start'));
    info_map.get('time_stop').value = info_map.get('date_formatter').format(info_map.get('date_stop'));
    info_map.get('time_duration').value = seconds_to_hh_mm(info_map.get('duration'));
}

function click_to_button(event) {
    let id = event.id;
    if (id == "accept") {
        update_info_in_bd();
    }
    close_element_to_edit();
}

function update_info_in_bd() {

}
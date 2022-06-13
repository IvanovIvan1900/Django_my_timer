let info_from_page = new Map();
let has_a_table = false;
let table_time_tracker = undefined;
let crf_token = undefined
document.addEventListener("DOMContentLoaded", action_after_load_page);

function action_after_load_page() {
    table_time_tracker = document.getElementById('time_track_list');
    info_from_page.set('curr_string_info', undefined)
    crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
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
    new_info_map.set('time_track_id', td.dataset.tt_id);
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
    new_info_map.set('td_date_start', td.parentNode.querySelector('td[id="td_date_start"]'));
    new_info_map.set('td_date_stop', td.parentNode.querySelector('td[id="td_date_stop"]'));

    new_info_map.get('time_start').onblur = change_part_of_time;
    new_info_map.get('time_stop').onblur = change_part_of_time;
    new_info_map.get('time_duration').onblur = change_part_of_time;
    new_info_map.get('href_time_duration').innerText = "";
    info_from_page.set('curr_string_info', new_info_map);

    refresh_data_in_input();
}

function service_date_format_to_represent(d) {
    // ("0" + d.getDate()).slice(-2) + "-" + ("0"+(d.getMonth()+1)).slice(-2) + "-" +
    // d.getFullYear() + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    return ("0" + d.getDate()).slice(-2) + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
}

function service_dat_format_to_inner(d) {
    return d.getFullYear() +
        "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2) + "_" + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + ":" + ("0" + d.getSeconds()).slice(-2);
}

function close_element_to_edit(update_html) {
    let info_map = info_from_page.get('curr_string_info');
    info_map.get('href_time_duration').innerText = seconds_to_hh_mm(info_map.get('duration'));
    info_map.get('div_edit').innerHTML = "";
    info_from_page.set('curr_string_info', undefined);
    if (update_html) {
        info_map.get('td_date_start').innerText = service_date_format_to_represent(info_map.get("date_start"));
        info_map.get('td_date_stop').innerText = service_date_format_to_represent(info_map.get("date_stop"));
        td = info_map.get("root_td");
        td.dataset.date_start = service_dat_format_to_inner(info_map.get("date_start"));
        td.dataset.date_stop = service_dat_format_to_inner(info_map.get("date_stop"));
        td.dataset.duration = info_map.get('duration');
    }
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
    update_html = false
    if (id == "accept") {
        update_info_in_bd();
        update_html = true
    }
    close_element_to_edit(update_html);
}

function toIsoString(date) {
    var tzo = -date.getTimezoneOffset(),
        dif = tzo >= 0 ? '+' : '-',
        pad = function(num) {
            return (num < 10 ? '0' : '') + num;
        };

    return date.getFullYear() +
        '-' + pad(date.getMonth() + 1) +
        '-' + pad(date.getDate()) +
        'T' + pad(date.getHours()) +
        ':' + pad(date.getMinutes()) +
        ':' + pad(date.getSeconds()) +
        dif + pad(Math.floor(Math.abs(tzo) / 60)) +
        ':' + pad(Math.abs(tzo) % 60);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function update_info_in_bd() {
    curr_string_info = info_from_page.get('curr_string_info')
    if ((crf_token != undefined) && (curr_string_info != undefined)) {
        let update_info = {
            "date_start": toIsoString(curr_string_info.get('date_start')),
            "date_stop": toIsoString(curr_string_info.get('date_stop'))
        };
        $.ajax({
            type: "PUT",
            url: "/api/tt/".concat(curr_string_info.get('time_track_id')).concat("/"),
            data: JSON.stringify(update_info),
            headers: {
                "Content-Type": "application/json",
                // "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"), // don't forget to include the 'getCookie' function
            }
            // success: (data) => {
            //     console.log(data);
            // },
            // error: (error) => {
            //     console.log(error);
            // }
        });
    }
}
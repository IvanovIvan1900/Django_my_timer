let date_start = undefined;
let date_stop = undefined;
let duration_sec = undefined;
let format_date = 'DD.MM.YYYY HH:mm';
let map_element = undefined;



document.addEventListener("DOMContentLoaded", action_after_load_page);

function action_after_load_page() {
    map_element = new Map()
    map_element.set("date_start", $('input[name="date_start"]'))
    map_element.set("date_stop", $('input[name="date_stop"]'))
    map_element.set("duration", $('input[name="duration_sec"]'))

    map_element.get('date_start').on("change", date_start_edit)
    map_element.get('date_stop').on("change", date_stop_edit)
    map_element.get('duration').on("change", duration_edit)

    map_element.get('duration')[0].type = 'time';

    map_element.get('date_start').trigger('change');
    map_element.get('date_stop').trigger('change');

    // переделаем элемент редактирования продолжительности под себя
}

function service_parse_date(str_date) {
    // ВАЖНО. Для работы данной функции нужна библиотека  moment.js
    return moment(str_date, format_date)
}

function service_recalculate_duration() {
    duration_in_sec = (date_stop - date_start) / 1000;
    map_element.get('duration')[0].value = seconds_to_hh_mm(duration_in_sec);

}

function date_start_edit(event) {
    date_start = service_parse_date(this.value);
    service_recalculate_duration();
}

function date_stop_edit(event) {
    date_stop = service_parse_date(this.value);
    service_recalculate_duration();
}

function duration_edit(event) {
    let part_time = event.currentTarget.value.split(':');
    date_stop = moment(date_start);
    date_stop.add(Number(part_time[0] * 3600 + Number(part_time[1]) * 60), 'seconds');
    map_element.get('date_stop')[0].value = moment(date_stop).format(format_date);
    service_recalculate_duration();
}

// function date_start_edit() {

// }
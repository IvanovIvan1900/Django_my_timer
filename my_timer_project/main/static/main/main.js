function seconds_to_hh_mm(time_delta_in_sec) {
    let hour_del = 3600;
    let min_del = 60;
    let sec = time_delta_in_sec;
    let hours = Math.floor(sec / hour_del);
    sec = sec % hour_del;
    let min = Math.floor(sec / min_del);
    let hours_str = ("0" + hours).slice(-2);
    let min_str = ("0" + min).slice(-2);
    let str_repr = `${hours_str}:${min_str}`;
    return str_repr;
}
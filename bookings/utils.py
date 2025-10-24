from datetime import timedelta


def slot_range(start_dt, duration_minutes: int):
    return start_dt, start_dt + timedelta(minutes=duration_minutes)


def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end

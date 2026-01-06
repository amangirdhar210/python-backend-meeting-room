import time


def is_time_range_valid(start: int, end: int) -> bool:
    return start < end


def overlaps(start1: int, end1: int, start2: int, end2: int) -> bool:
    return start1 < end2 and start2 < end1


def is_within_booking_window(start_time: int, max_days_in_future: int) -> bool:
    current_time = int(time.time())
    max_future_time = current_time + (max_days_in_future * 24 * 60 * 60)
    return start_time >= current_time and start_time <= max_future_time

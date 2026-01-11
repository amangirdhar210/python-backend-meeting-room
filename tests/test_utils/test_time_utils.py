import pytest
import time
from app.utils import time_utils


class TestTimeUtils:

    def test_is_time_range_valid_valid_range(self):
        start = 1704800000
        end = 1704803600

        result = time_utils.is_time_range_valid(start, end)

        assert result is True

    def test_is_time_range_valid_invalid_range(self):
        start = 1704803600
        end = 1704800000

        result = time_utils.is_time_range_valid(start, end)

        assert result is False

    def test_is_time_range_valid_equal_times(self):
        timestamp = 1704800000

        result = time_utils.is_time_range_valid(timestamp, timestamp)

        assert result is False

    def test_is_time_range_valid_one_second_difference(self):
        start = 1704800000
        end = 1704800001

        result = time_utils.is_time_range_valid(start, end)

        assert result is True

    def test_overlaps_complete_overlap(self):
        result = time_utils.overlaps(1000, 2000, 1000, 2000)

        assert result is True

    def test_overlaps_partial_overlap_start(self):
        result = time_utils.overlaps(1000, 1500, 1200, 1800)

        assert result is True

    def test_overlaps_partial_overlap_end(self):
        result = time_utils.overlaps(1200, 1800, 1000, 1500)

        assert result is True

    def test_overlaps_one_contains_other(self):
        result = time_utils.overlaps(1000, 2000, 1200, 1800)

        assert result is True

    def test_overlaps_no_overlap_before(self):
        result = time_utils.overlaps(1000, 1200, 1300, 1500)

        assert result is False

    def test_overlaps_no_overlap_after(self):
        result = time_utils.overlaps(1300, 1500, 1000, 1200)

        assert result is False

    def test_overlaps_adjacent_times_no_overlap(self):
        result = time_utils.overlaps(1000, 1200, 1200, 1400)

        assert result is False

    def test_overlaps_touching_at_boundary(self):
        result = time_utils.overlaps(1000, 1500, 1500, 2000)

        assert result is False

    def test_is_within_booking_window_current_time(self):
        current = int(time.time())

        result = time_utils.is_within_booking_window(current, 30)

        assert result is True

    def test_is_within_booking_window_future_valid(self):
        current = int(time.time())
        future = current + (15 * 24 * 60 * 60)

        result = time_utils.is_within_booking_window(future, 30)

        assert result is True

    def test_is_within_booking_window_at_max_boundary(self):
        current = int(time.time())
        max_days = 30
        future = current + (max_days * 24 * 60 * 60)

        result = time_utils.is_within_booking_window(future, max_days)

        assert result is True

    def test_is_within_booking_window_past_time(self):
        current = int(time.time())
        past = current - (1 * 24 * 60 * 60)

        result = time_utils.is_within_booking_window(past, 30)

        assert result is False

    def test_is_within_booking_window_too_far_future(self):
        current = int(time.time())
        far_future = current + (31 * 24 * 60 * 60)

        result = time_utils.is_within_booking_window(far_future, 30)

        assert result is False

    def test_is_within_booking_window_zero_days(self):
        current = int(time.time())
        future = current + 100

        result = time_utils.is_within_booking_window(future, 0)

        assert result is False

    def test_is_within_booking_window_one_day(self):
        current = int(time.time())
        tomorrow = current + (1 * 24 * 60 * 60)

        result = time_utils.is_within_booking_window(tomorrow, 1)

        assert result is True

    def test_is_within_booking_window_one_second_over(self):
        current = int(time.time())
        max_days = 30
        just_over = current + (max_days * 24 * 60 * 60) + 1

        result = time_utils.is_within_booking_window(just_over, max_days)

        assert result is False

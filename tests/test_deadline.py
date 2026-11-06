from app import store


def test_due_today():
    assert store.deadline_status("2026-11-06", "2026-11-06") == "due today"


def test_overdue_one_day():
    assert store.deadline_status("2026-11-06", "2026-11-07") == "overdue by 1 day"


def test_overdue_several_days():
    assert store.deadline_status("2026-11-06", "2026-11-10") == "overdue by 4 days"


def test_due_in_future():
    assert store.deadline_status("2026-11-06", "2026-11-04") == "due in 2 days"


def test_dispute_line_carries_status_when_today_is_set():
    line = store.CustomerScope("C001", today="2026-11-07").record_lines()["D-1001"]
    assert "deadline status: overdue by 1 day (as of 2026-11-07)" in line


def test_dispute_line_without_today_has_no_status():
    line = store.CustomerScope("C001").record_lines()["D-1001"]
    assert "deadline status" not in line


def test_closed_disputes_get_no_deadline_status():
    resolved = store.CustomerScope("C020", today="2026-10-30").record_lines()["D-1004"]  # resolved_in_favour
    declined = store.CustomerScope("C006", today="2026-10-30").record_lines()["D-1002"]  # declined
    assert "deadline status" not in resolved
    assert "deadline status" not in declined

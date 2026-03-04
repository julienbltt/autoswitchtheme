import pytest
import schedule


@pytest.fixture(autouse=True)
def clear_schedule_jobs():
    """Clear all schedule jobs before and after each test to prevent leakage."""
    schedule.clear()
    yield
    schedule.clear()

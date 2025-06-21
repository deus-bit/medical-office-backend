from pydantic import BaseModel, Field, ValidationError
from datetime import date, datetime
from app.utils import (
    NumberInterval, IntInterval, FloatInterval, DateInterval, DatetimeInterval,
    RegEx
)
import pytest
import re

class TestModel(BaseModel):
    # Mark this class as not a test class to prevent pytest collection warnings.
    # For more info: https://docs.pytest.org/en/latest/example/pythoncollection.html#customizing-test-collection
    __test__ = False
    number_interval: NumberInterval
    int_interval: IntInterval
    float_interval: FloatInterval
    date_interval: DateInterval
    datetime_interval: DatetimeInterval


@pytest.mark.parametrize(
    "interval_type, value",
    [
        # NumberInterval
        (NumberInterval, "[0,10]"),
        (NumberInterval, "(-inf,inf)"),
        (NumberInterval, "[5,5]"),
        (NumberInterval, "[1, 2.0]"),

        # IntInterval
        (IntInterval, "[0,10]"),
        (IntInterval, "(-inf,inf)"),
        (IntInterval, "[5,5]"),

        # FloatInterval
        (FloatInterval, "[0.0,10.0]"),
        (FloatInterval, "(-inf,inf)"),
        (FloatInterval, "[5.5,5.5]"),

        # DateInterval
        (DateInterval, "[2023-01-01,2023-12-31]"),
        (DateInterval, "(-inf,inf)"),
        (DateInterval, "[2023-07-15,2023-07-15]"),
        (DateInterval, "[2024-02-29,2024-03-01]"), # Leap year

        # DatetimeInterval
        (DatetimeInterval, "[2023-01-01T00:00:00,2023-01-01T23:59:59]"),
        (DatetimeInterval, "(-inf,inf)"),
        (DatetimeInterval, "[2023-07-15T12:30:00.000,2023-07-15T12:30:00.000]"), # Single point datetime
        (DatetimeInterval, "(2023-01-01T00:00:00.123,2023-01-01T23:59:59.987)"), # Microseconds
    ]
)
def test_valid_intervals(interval_type, value):
    """Test that valid interval strings are accepted by Pydantic."""
    field_name = interval_type.__name__.lower().replace("interval", "_interval")
    data = {
        "number_interval": "[0,1]",
        "int_interval": "[0,1]",
        "float_interval": "[0.0,1.0]",
        "date_interval": "[2000-01-01,2000-01-02]",
        "datetime_interval": "[2000-01-01T00:00:00,2000-01-01T00:00:01]"
    }
    data[field_name] = value
    try:
        TestModel(**data)
    except ValidationError as e:
        pytest.fail(f"Validation failed for valid interval '{value}' of type {interval_type.__name__}: {e}")

@pytest.mark.parametrize(
    "interval_type, value, expected_error_msg_part",
    [
        # Common Format Errors (caught by regex Field pattern)
        (NumberInterval, "0,10", "Invalid interval string format"), # Missing brackets
        (FloatInterval, "[0.0;10.0]", "Invalid interval string format"), # Wrong separator
        (DateInterval, "[2023-01-01,2023-12-31", "Invalid interval string format"), # Missing closing bracket
        (DatetimeInterval, "2023-01-01T00:00:00,2023-01-01T23:59:59]", "Invalid interval string format"), # Missing opening bracket

        # Invalid Value Format (caught by parse_value's try-except)
        (NumberInterval, "[abc,10]", "Invalid number format"), # 'abc' doesn't fit NUMBER regex
        (IntInterval, "[0,10.5]", "Invalid integer format"), # '10.5' doesn't fit INTEGER regex
        (DateInterval, "[2023-13-01,2023-12-31]", "Invalid date format"), # Date format is valid by regex, but month is invalid. parse_value will catch.
        (DatetimeInterval, "[2023-01-01T25:00:00,2023-01-01T23:59:59]", "Invalid datetime format"), # Datetime format is valid by regex, but hour is invalid. parse_value will catch.

        # Invalid Order (start > end - caught by `is_greater_than` check)
        (NumberInterval, "[10,0]", "Start value (10) must be less than or equal to end value (0)"),
        (NumberInterval, "(inf,0]", "Start value (inf) must be less than or equal to end value (0)"),
        (NumberInterval, "[0,-inf)", "Start value (0) must be less than or equal to end value (-inf)"),
        (DateInterval, "[2023-01-02,2023-01-01]", "Start value (2023-01-02) must be less than or equal to end value (2023-01-01)"),
        (DatetimeInterval, "(inf,2023-01-01T10:00:00]", "Start value (inf) must be less than or equal to end value (2023-01-01T10:00:00)"),

        # Invalid 'inf' Closure (caught by specific `inf` closure checks)
        (NumberInterval, "[inf,10)", "Interval starting with 'inf' must use an open bracket '('"),
        (NumberInterval, "(0,inf]", "Interval ending with 'inf' must use an open bracket ')'"),
        (DateInterval, "[inf,2023-01-01)", "Interval starting with 'inf' must use an open bracket '('"),
        (DatetimeInterval, "(2023-01-01T00:00:00,inf]", "Interval ending with 'inf' must use an open bracket ')'"),
    ]
)
def test_invalid_intervals(interval_type, value, expected_error_msg_part):
    """Test that invalid interval strings raise ValidationError with expected message."""
    field_name = interval_type.__name__.lower().replace("interval", "_interval")
    data = {
        "number_interval": "[0,1]",
        "int_interval": "[0,1]",
        "float_interval": "[0.0,1.0]",
        "date_interval": "[2000-01-01,2000-01-02]",
        "datetime_interval": "[2000-01-01T00:00:00,2000-01-01T00:00:01]"
    }
    data[field_name] = value

    with pytest.raises(ValidationError) as excinfo:
        TestModel(**data)

    assert any(expected_error_msg_part in str(err) for err in excinfo.value.errors()), \
           f"Expected '{expected_error_msg_part}' in errors for '{value}', but got: {excinfo.value.errors()}"


def test_regex_direct_instantiation_valid():
    valid_pattern = r"^\d{3}-\d{2}-\d{4}$"
    regex_obj = RegEx(valid_pattern)

    assert isinstance(regex_obj, RegEx)
    assert regex_obj == valid_pattern
    assert str(regex_obj) == valid_pattern
    assert regex_obj.is_match("123-45-6789") is True

def test_regex_direct_instantiation_invalid_syntax():
    invalid_pattern = r"([a-z]+"
    with pytest.raises(ValueError, match="Invalid regular expression"):
        RegEx(invalid_pattern)

    invalid_pattern_2 = r"*\d"
    with pytest.raises(ValueError, match="Invalid regular expression"):
        RegEx(invalid_pattern_2)

def test_regex_direct_instantiation_non_string_type():
    with pytest.raises(TypeError, match="Expected a string for regex pattern"):
        RegEx(123)
    with pytest.raises(TypeError, match="Expected a string for regex pattern"):
        RegEx(None)
    with pytest.raises(TypeError, match="Expected a string for regex pattern"):
        RegEx(["list", "of", "strings"])

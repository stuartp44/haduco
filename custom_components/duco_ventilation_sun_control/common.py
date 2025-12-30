def _process_node_temperature(value: float | None) -> float | None:
    """Process node temperature values."""
    if value is not None:
        return value  # Assuming value is in Celsius
    return None


def _process_node_humidity(value: float | None) -> float | None:
    """Process node humidity values."""
    if value is not None:
        return value  # Assuming value is in percentage
    return None


def _process_node_co2(value: float | None) -> float | None:
    """Process node CO₂ values."""
    if value is not None:
        return value  # Assuming value is in ppm
    return None


def _process_node_iaq(value: float | None) -> float | None:
    """Process node IAQ values."""
    if value is not None:
        return value  # Assuming value is in percentage
    return None


# Main sensor processing functions
def _process_temperature(value: float | None) -> float | None:
    """Process temperature values by dividing by 10."""
    if value is not None:
        return value / 10.0  # Convert from tenths of degrees Celsius
    return None


def _process_speed(value: float | None) -> float | None:
    """Process speed values."""
    if value is not None:
        return value  # Assuming value is already in RPM
    return None


def _process_pressure(value: float | None) -> float | None:
    """Process pressure values."""
    if value is not None:
        return value  # Assuming value is in Pa
    return None


def _process_rssi(value: float | None) -> float | None:
    """Process Wi-Fi signal strength."""
    if value is not None:
        return value  # Assuming value is in dBm
    return None


def _process_uptime(value: float | None) -> float | None:
    """Process device uptime."""
    if value is not None:
        return value  # Assuming value is in seconds
    return None


def _process_timefilterremain(value: float | None) -> float | None:
    """Process filter time remaining."""
    if value is not None:
        return value  # Assuming value is in days
    return None


def _process_bypass_position(value: float | None) -> int | None:
    """Process bypass position."""
    if value is not None:
        # Assuming value ranges from 0 to 255, where 255 is 100%
        return round((value / 255) * 100)
    return None


def _process_network_status(value: str | None) -> str | None:
    """Process network status."""
    if value is not None:
        return value.title()  # Assuming value is a string
    return None


def _process_calibration_status(value: bool | None) -> str | None:
    """Process calibration status."""
    if value is not None:
        if value:
            return "Valid"
        else:
            return "Invalid"
    return None


def _process_calibration_state(value: str | None) -> str | None:
    """Process calibration state."""
    if value is not None:
        return value.title()  # Assuming value is a string
    return None

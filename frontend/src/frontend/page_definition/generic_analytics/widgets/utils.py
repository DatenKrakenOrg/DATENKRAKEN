from enum import Enum

sensor_data_language_dict = {
    "Temperatur": "temperature_inside",
    "Luftfeuchtigkeit": "humidity_inside",
    "Luftqualität (Voc-Index)": "voc_index",
    "Lautstärke": "noise_level",
}
class SensorStatus(Enum):
    OPTIMAL = 0,
    WARNING = 1,
    CRITICAL = 2

def get_status(value, param_name, config) -> SensorStatus:
    """Evaluate the status of a sensor reading against configured thresholds.

    The function checks the given value against the parameter configuration
    loaded in the global `config` dictionary. Each parameter defines an
    optimal range and a tolerance. The returned status is determined as:

        - "optimal": Value is within the defined optimal range.
        - "warning": Value is outside the optimal range but within the
          tolerance margin.
        - "critical": Value is outside both the optimal range and tolerance.
        - "unknown": If the parameter is not defined in the configuration.

    Args:
        value (int | float): The sensor reading to evaluate.
        param_name (str): The name of the parameter to look up in config,
            e.g. "temperature_inside", "humidity_inside", "voc_index",
            "noise_level".

    Returns:
        SensorStatus: One of SensorStatus."""
    param_cfg = config["parameters"][param_name]
    if not param_cfg:
        return "unknown"

    min_opt = param_cfg["optimal_range"]["min"]
    max_opt = param_cfg["optimal_range"]["max"]
    tolerance = param_cfg["tolerance"]

    if min_opt <= value <= max_opt:
        return SensorStatus.OPTIMAL
    elif (min_opt - tolerance) <= value <= (max_opt + tolerance):
        return SensorStatus.WARNING
    else:
        return SensorStatus.CRITICAL
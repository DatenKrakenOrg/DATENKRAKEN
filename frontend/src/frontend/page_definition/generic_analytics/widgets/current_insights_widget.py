import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple

def gauge_plot(value: float, title: str, value_range: Tuple[float], bar_color: str, unit: str) -> go.Figure:
    """Create a Plotly gauge chart for visualizing a single sensor value.

    The gauge displays the given value within a defined range and uses a
    colored bar to indicate its position. A numeric label with a unit is also
    shown inside the gauge.

    Args:
        value (float): The numeric value to display.
        title (str): Title of the gauge (e.g., parameter name).
        value_range (Tuple[float]): Two-element list [min, max] defining the axis range. Defined in parameter.json.
        bar_color (str): Color of the gauge's bar (e.g., "green", "red").
        unit (str): Measurement unit displayed next to the value (e.g., "°C"). Defined in parameter.json.

    Returns:
        go.Figure: A Plotly figure object containing the gauge visualization."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": f" {unit}"},
            title={"text": title},
            gauge={
                "axis": {"range": value_range, "tickcolor": "gray"},
                "bgcolor": "lightgray",
                "bar": {"color": bar_color, "thickness": 1},
                "steps": [{"range": value_range, "color": "lightgray"}],
            },
        )
    )
    fig.update_layout(width=250, height=250, margin=dict(l=20, r=28, t=50, b=20))
    return fig
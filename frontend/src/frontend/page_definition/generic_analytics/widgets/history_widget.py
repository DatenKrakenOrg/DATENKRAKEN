import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta, timezone  # new changes
from utility.datafetcher import DataFetcher
from database.orm import SensorType

def show_timeline_widget(sensor_type: SensorType, arduino_id: str, time_delta: timedelta, fetcher: DataFetcher, unit: str):
    """Shows all history related widget based on a sensor_type and a arduino_id (room)

    Args:
        sensor_type (SensorType): Sensor that should be fetched
        arduino_id (str): Arduino ID (Room) to fetch from
        time_delta (timedelta): Timedelta which is used for start and end data (Intervall: [NOW - timedelta, NOW])
        fetcher (DataFetcher): DataFetcher used to fetch data from database
        unit (str): Unit used for y axis
    """
    #new changes Use timezone-aware UTC to match DB timestamps
    current_datetime = datetime.now(timezone.utc)
    #new changes Guard DB fetching to provide clear feedback instead of breaking the page
    try:
        history_df = fetcher.get_bucket_by_t_interval(sensor_type, arduino_id, current_datetime - time_delta, current_datetime)
    except Exception:
        st.error("Could not load time series from the database.")
        return
    min_value = history_df["avg_value_in_bucket"].min()
    max_value = history_df["avg_value_in_bucket"].max()
    
    if len(history_df) != 0:
        # Quickfix for correct time in plotly. Since its aware of summer / winter times but offsetted by 2 hours..
        history_df["bucket_time"] = history_df["bucket_time"] + timedelta(hours=2)
        y_min_sel, y_max_sel = st.slider(
            "Anzeigebereich (min/max)",
            min_value=float(round(min_value, 2)),
            max_value=float(round(max_value, 2)),
            value=(float(round(min_value, 2)), float(round(max_value, 2))),
            step=0.01,
            help="Lege den sichtbaren Wertebereich der y-Achse fest.",
        )

        fig_line = px.line(
            history_df, x="bucket_time", y="avg_value_in_bucket",
            labels={"time": "Zeit", "value": f"Wert ({unit})"}
        )
        fig_line.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode="x unified",
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(buttons=[
                    dict(count=24, label="24h", step="hour", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(count=30, label="30d", step="day", stepmode="backward"),
                    dict(step="all", label="Alle"),
                ]),
            ),
        )
        fig_line.update_yaxes(range=[y_min_sel, y_max_sel])
        st.plotly_chart(fig_line)
    else:
        st.warning("Oops! Seems like there was no measurement found in your specified time period..")
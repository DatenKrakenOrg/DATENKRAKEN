import streamlit as st
from frontend.page_definition import render_overview
from frontend.page_definition.generic_analytics import define_generic_analytics_page
from frontend import ROOMS, FETCHER, CONFIG


def main():
    """Streamlit app entry point for displaying room sensor overviews."""
    arduino_ids_unpacked_from_sensor = [room for room in ROOMS.values()]
    unique_arduino_ids = set(room for room_list in arduino_ids_unpacked_from_sensor for room in room_list)

    pages = [
    st.Page(
        lambda: render_overview(unique_arduino_ids, FETCHER, CONFIG),
        title="Overview",
        url_path="overview",
        default=True,
    ),
    *[
        st.Page(
            (lambda aid=aid: lambda: define_generic_analytics_page(aid, FETCHER, CONFIG))(),
            title=f"Raum {aid}",
            url_path=f"room_{aid}",
        )
        for aid in unique_arduino_ids
    ],
    ]

    pg = st.navigation(pages)
    pg.run()






if __name__ == "__main__":
    main()

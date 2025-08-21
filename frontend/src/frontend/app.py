import streamlit as st
from frontend.page_definition import render_overview


def main():
    """Streamlit app entry point for displaying room sensor overviews."""
    st.set_page_config(layout="wide")
    render_overview()


if __name__ == "__main__":
    main()

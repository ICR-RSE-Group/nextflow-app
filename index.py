import streamlit as st

st.set_page_config(
    page_icon="🍃",
    page_title="run-nextflow on Alma",
    layout="wide",
    initial_sidebar_state="auto",
)


def main():
    p1 = st.Page("views/login.py")
    p2 = st.Page("views/run_pipeline.py")
    nav_pages = [p1, p2]
    pages = {"p1": p1, "p2": p2}
    st.session_state["pages"] = pages
    pg = st.navigation(nav_pages)
    pg.run()


if __name__ == "__main__":
    main()

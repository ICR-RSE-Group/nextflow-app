import streamlit as st


def header():
    header = """
        <span style=
        "color:darkred;font-size:40px;"> -🍃 </span><span style=
        "color:green;font-size:40px;">RUN NEXTFLOW on ALMA</span><span style=
        "color:darkred;font-size:40px;">🍃- </span>
        """
    st.markdown(header, unsafe_allow_html=True)

    st.write("---  ")

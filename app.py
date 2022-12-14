from datetime import datetime
import time
import pandas as pd
import streamlit as st
import numpy as np
import openpyxl

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Data Accuracy check - JUYO", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")

hide_default_format = """
       <style>
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)




# Header of page
with st.container():

    l_column, m_column, r_column = st.columns((3))
    
    with l_column:
        st.write("")
    
    with m_column:
        st.write(
            """
        # 📊 Data accuracy check
        Upload the 'Exploration By Day' and the XML file from the database.
        """
        )
    
    with r_column:
        st.write("")

with st.container():

    st.write("---")

    left_column, right_column = st.columns(2)

    with left_column:
        st.header("Exploration By Day")
        uploaded_file_JUYO = st.file_uploader("Upload JUYO file", type=".xlsx")

        use_example_file = st.checkbox(
            "Use example file", False, help="Use in-built example file to demo the app")

        if use_example_file:
            uploaded_file_JUYO = 'Exploration by day 2022-11-29 (1).xlsx'

        if uploaded_file_JUYO:
            df = pd.read_excel(uploaded_file_JUYO)
            st.markdown("### Data preview")
            st.dataframe(df.head())

            '## Select columns for data check'
            'Standard = OTB & otb_rev, only change this when header names have changed'
            'Currently the multiselect is disabled, due to code not ready to recongnize the different columns'
            disabled = 1
            cols = st.multiselect('select columns:', df.columns, default=["OTB", "otb_rev"], disabled=disabled)

            st.write('You selected:', cols)

    with right_column:
        st.header("XML file database")
        uploaded_file_XML = st.file_uploader("Upload XML file", type=".xlsx")

        use_example_file1 = st.checkbox(
            "Use example file1", False, help="Use in-built example file to demo the app")

        if use_example_file1:
            uploaded_file_XML = 'Hotel1 XML.xlsx'

        if uploaded_file_XML:
            df1 = pd.read_excel(uploaded_file_XML)
            df1.round(1)
            st.markdown("### Data preview")
            st.dataframe(df1.head())

            '## Select columns for data check'
            'Standard are already selected, only change this when header names have changed'
            cols1 = st.multiselect('select columns:', df1.columns, default=["IND_DEDUCT_ROOMS", "GRP_DEDUCT_ROOMS", "IND_DEDUCT_REVENUE", "GRP_DEDUCT_REVENUE"], disabled=disabled)
            st.write('You selected:', cols1)

            st.write(f"Data accuracy check will begin from date: {df1['CONSIDERED_DATE'].iloc[0]}")

            st.write(f"The first selection = {cols1[0]}")

st.write("---")

if st.button('submit'): run_report()
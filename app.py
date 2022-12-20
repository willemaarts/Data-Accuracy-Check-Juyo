import sys, os
import traceback
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
import numpy as np
from PIL import Image
import altair as alt
import locale

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
im = Image.open('images/JUYOcon.ico')
st.set_page_config(page_title="Data Accuracy check - JUYO", page_icon=im, layout="wide", initial_sidebar_state="collapsed")

hide_default_format = """
       <style>
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

def run_XML_transer():
    # parse the XML file
    try:
        tree = ET.parse(uploaded_file_XML)

        root = tree.getroot()

        # Elements to search in XML file
        element_path = ["CONSIDERED_DATE", "IND_DEDUCT_ROOMS", "GRP_DEDUCT_ROOMS", "IND_DEDUCT_REVENUE", "GRP_DEDUCT_REVENUE"]

        # create an empty list
        data_date = []
        data_IND_Rs = []
        data_GRP_Rs = []
        data_IND_Rv = []
        data_GRP_Rv = []

        # define the XPath expression to extract the data we want
        xpath_date = f'.//G_CONSIDERED_DATE/{element_path[0]}'
        xpath_IND_Rs = f'.//G_CONSIDERED_DATE/{element_path[1]}'
        xpath_GRP_Rs = f'.//G_CONSIDERED_DATE/{element_path[2]}'
        xpath_IND_Rv = f'.//G_CONSIDERED_DATE/{element_path[3]}'
        xpath_GRP_Rv = f'.//G_CONSIDERED_DATE/{element_path[4]}'

        # iterate over each element that matches the XPath expression
        for (element_date, element_IND_Rs, element_GRP_Rs, element_IND_Rv, element_GRP_Rv) in zip(root.findall(xpath_date), root.findall(xpath_IND_Rs), root.findall(xpath_GRP_Rs), root.findall(xpath_IND_Rv), root.findall(xpath_GRP_Rv)):
            # extract the text of each element and append to the list
            data_date.append(element_date.text)
            data_IND_Rs.append(element_IND_Rs.text)
            data_GRP_Rs.append(element_GRP_Rs.text)
            data_IND_Rv.append(element_IND_Rv.text)
            data_GRP_Rv.append(element_GRP_Rv.text)

        # convert the list to a pandas dataframe
        df = pd.DataFrame()
        df[f'{element_path[0]}'] = data_date

        df[f'{element_path[1]}'] = data_IND_Rs
        df[f'{element_path[1]}'] = pd.to_numeric(df[f'{element_path[1]}'])

        df[f'{element_path[2]}'] = data_GRP_Rs
        df[f'{element_path[2]}'] = pd.to_numeric(df[f'{element_path[2]}'])

        df[f'{element_path[3]}'] = data_IND_Rv
        df[f'{element_path[3]}'] = pd.to_numeric(df[f'{element_path[3]}'])

        df[f'{element_path[4]}'] = data_GRP_Rv
        df[f'{element_path[4]}'] = pd.to_numeric(df[f'{element_path[4]}'])

        xml_dataframe = df

        return xml_dataframe

    except Exception as e:
        
        traceback.print_exc()

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        st.error(f'Err4: {exc_type}; {exc_obj}; ({str(e)}), line: {exc_tb.tb_lineno}, in {fname}')
        return

def run_check():
    with st.spinner('running process...'): 

        try:
            locale.setlocale(locale.LC_ALL, '') # Use '' for auto, or force e.g. to 'nl_NL.UTF-8' 

            element_path = ["CONSIDERED_DATE", "IND_DEDUCT_ROOMS", "GRP_DEDUCT_ROOMS", "IND_DEDUCT_REVENUE", "GRP_DEDUCT_REVENUE"]
            
            output = pd.DataFrame([JUYO_DF['date']]).transpose()
            output['date'] = pd.to_datetime(output['date'])

            output['OTB_XML'] = XML_DF[f'{element_path[1]}'] +  XML_DF[f'{element_path[2]}']
            output['OTB_JUYO'] = JUYO_DF['OTB']
            output['OTB_DIFF'] = abs(output['OTB_XML'] - output['OTB_JUYO'])
            
            output['OTB_%'] = output['OTB_XML'] / output['OTB_JUYO'] * 100

            output['OTB_%'] = np.where(output['OTB_%'] >= 100, output['OTB_JUYO'] / output['OTB_XML'] * 100, output['OTB_XML'] / output['OTB_JUYO'] * 100)
            
            output['REV_XML'] = abs(XML_DF[f'{element_path[3]}'] + XML_DF[f'{element_path[4]}'])
            output['REV_JUYO'] = abs(JUYO_DF['otb_rev'])
            output['REV_DIFF'] = abs(output['REV_XML'] - output['REV_JUYO'])

            output['REV_%'] = output['REV_XML'] / output['REV_JUYO'] * 100

            output['REV_%'] = np.where(output['REV_%'] >= 100, output['REV_JUYO'] / output['REV_XML'] * 100, output['REV_XML'] / output['REV_JUYO'] * 100)            
            
            total_rn = int(output['OTB_DIFF'].sum())
            total_rev = int(output['REV_DIFF'].sum())
            mean_rev = round((output['REV_%'].mean()),3)
            mean_OTB = round((output['OTB_%'].mean()),3)

            st.subheader(f'Data accuracy check period from {date_JUYO} till {date_last}')

            l_column, m_column, r_column = st.columns(3)

            with l_column:
                st.subheader("🏨 Total discrepancies Rn's:")
                st.metric("RN's",f'{total_rn:n}')

            with m_column:
                st.subheader("💲 Total discrepancies REV:")
                st.metric("REV",f"€ {total_rev:n}") 

            with r_column:
                st.markdown('### 📝 Average accuracy:')
                st.metric("Revenue accuracy",f"{mean_rev:n} %") 

                st.metric("OTB accuracy",f"{mean_OTB:n} %")

            source = pd.DataFrame({
                'difference OTB': output['OTB_DIFF'],
                'date': output['date'],
                'mean': output['OTB_%']
                })
        
            c = alt.Chart(source).mark_bar().encode(
                x='date',
                y='difference OTB',
                tooltip=['difference OTB', 'date', 'mean']
                ) 

            rule = alt.Chart(source).mark_rule(color='red').encode(
                alt.Y('mean(mean)',
                    scale=alt.Scale(domain=(1, 100)))
                )

            f = alt.layer(c, rule).resolve_scale(y='independent')

            st.subheader('Difference by day')
            st.altair_chart(f, use_container_width=True)

            output = output.drop('REV_%', axis=1)
            output = output.drop('OTB_%', axis=1)

            output.loc[:, "REV_DIFF"] = output["REV_DIFF"].map('{:.2f}'.format)
            output.loc[:, "REV_XML"] = output["REV_XML"].map('{:.2f}'.format)

            output

            output.to_excel("output.xlsx",index=False)

        except Exception as e:
        
            traceback.print_exc()

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            st.error(f'Err4: {exc_type}; {exc_obj}; ({str(e)}), line: {exc_tb.tb_lineno}, in {fname}')
            return

    st.success('Data accuracy check done', icon='✅')
    
    my_expander = st.expander(label='Expand me for text explanation for client')
    with my_expander:
        st.write(f'''
        The data accuracy of the period {date_JUYO} till {date_last} has been reviewed. 
        
        A total of {total_rn:n} room night discrepancies and €{total_rev:n} in revenue were identified. 
        
        The average revenue accuracy percentage for this period was {mean_rev:n}%, 
        and the average OTB accuracy percentage was {mean_OTB:n}%.
        ''')
    
    with open("output.xlsx", "rb") as file:
        st.download_button(
            label="click me to download excel",
            data=file,
            file_name=f'output data accuracy.xlsx',
            mime="application/octet-stream"
            )

# Header of the page
with st.container():
    
    l_column, m_column, r_column = st.columns([3,5,1])
    
    with l_column:
        st.write("")
    
    with m_column:
        st.write(
            """
        # 📊 Data accuracy check
        """
        )
    
    with r_column:
        imagejuyo = Image.open('images/JUYO3413_Logo_Gris1.png')
        st.image(imagejuyo)

# Here will start the step-by-step process for data input.
with st.container():

    st.write("---")
    disabled = 1

    left_column, right_column = st.columns(2)

    with left_column:

        st.header("Exploration By Day")
        st.checkbox('Upload different file?', disabled=disabled)

        uploaded_file_JUYO = st.file_uploader("Upload JUYO file", type=".xlsx")

        if uploaded_file_JUYO:
            
            JUYO_DF = pd.read_excel(uploaded_file_JUYO)
            
            st.markdown("### Data preview; Exploration by Day")
            
            st.dataframe(JUYO_DF.head())
        
        with right_column:
            st.header("XML file database")

            type = st.checkbox('Upload a Excel file instead of XML file?')
            
            if type:
                uploaded_file_XML = st.file_uploader("Upload XML file", type=".xlsx")
            else:
                uploaded_file_XML = st.file_uploader("Upload XML file", type=".XML")

            if uploaded_file_XML:
                
                if type:
                    XML_DF = pd.read_excel(uploaded_file_XML)
                else:    
                    XML_DF = run_XML_transer()

                st.markdown("### Data preview; XML file")
                st.dataframe(XML_DF.head())

    if uploaded_file_JUYO and uploaded_file_XML:

        st.write("---")

        obj_string = JUYO_DF['date'].iloc[-1]
        date_time_obj = datetime.datetime.strptime(XML_DF['CONSIDERED_DATE'][0], '%d-%b-%y')    
        date_time_obj1 = datetime.datetime.strptime(JUYO_DF['date'][0], '%Y-%m-%d')
        date_time_obj2 = datetime.datetime.strptime(obj_string, '%Y-%m-%d')
        
        date_JUYO = date_time_obj1.date()
        date_XML = date_time_obj.date()
        date_last = date_time_obj2.date()

        if date_JUYO == date_XML:
            if st.button('Start check'): run_check()
        else:
            st.warning(f'''
                ##### The dates the first row of both the files needs to be the same.
                ###### JUYO file = {date_JUYO} | XML file = {date_XML}\\
                Make sure that on the first row, both the dates are the same.
                ''', 
                icon='⚠️')
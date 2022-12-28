from xml.etree import ElementPath
import pandas as pd
import xml.etree.ElementTree as ET

from app import JUYO_DF, XML_DF

# parse the XML file
tree = ET.parse('md_juyo_history_forecast_BELAMI_20221206_9560255_2022-12-06_070221.xml')
root = tree.getroot()

# create an empty list
data = []
data1 = []
data2 = []

# define the XPath expression to extract the data we want
xpath_date = './/G_CONSIDERED_DATE/CONSIDERED_DATE'
xpath_occ = './/G_CONSIDERED_DATE/TOTAL_OCC'
xpath1_rev = './/G_CONSIDERED_DATE/ROOM_REVENUE'

# iterate over each element that matches the XPath expression
for (element_d, element_o, element_r) in zip(root.findall(xpath_date), root.findall(xpath_occ), root.findall(xpath1_rev)):
    # extract the text of each element and append to the list
    data.append(element_d.text)
    data1.append(element_o.text)
    data2.append(element_r.text,)

# convert the list to a pandas dataframe
df = pd.DataFrame()
df['date'] = data
df['occ'] = data1
df['rev'] = data2

# print the dataframe
print(df)

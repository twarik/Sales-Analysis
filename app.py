#Import necesssay libraries
import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Paired12, Category20_20
from bokeh.transform import factor_cmap

import warnings
warnings.filterwarnings('ignore')

#Define tools to add on the plots
TOOLS = 'pan,zoom_out,box_zoom,reset,save'

st.sidebar.markdown('''# Sales Analysis''')

#@st.cache_data(allow_output_mutation=True)
@st.cache_data()
def load_data():
    '''
    Function to read-in the dataset
    '''
    return pd.read_csv('./sales_data.csv')

def create_figure(x_label,y_label,height,TOOLS,x_type=None,x_ticks=None,title=None):
    '''
    Function to Create a new figure for plotting.
    '''
    if x_type==None:
        fig = figure(tools = TOOLS, title=title,
                    x_axis_label=x_label, y_axis_label=y_label,
                    height=height, x_range=x_ticks
                    )
    else:
        fig = figure(tools = TOOLS, title=title,
                    x_axis_label=x_label, y_axis_label=y_label,
                    height=height, x_axis_type=x_type
                    )
    return fig

def hover(tips):
    '''
    Function to create a hoover inspector tool
    '''
    tool = HoverTool()
    tool.tooltips=tips
    return tool

data = load_data()

#----------------------DATA CLEANING-------------------------------------------
data['Order Date'] = pd.to_datetime(data['Order Date'])
#----------------------FEATURE ENGINEERING-------------------------------------
#Add columns for date, hour, month,
data['hour']=data['Order Date'].dt.hour
data['Date']=data['Order Date'].dt.date
data['month']=data['Order Date'].dt.month
#Add a column for sales (sales = Quantity Ordered * Price Each)
data['Sales'] = data['Quantity Ordered'] * data['Price Each']

status = st.sidebar.radio('',('Home',
                              'What were the best and worst months for sales?',
                              'Which cities had the highest and lowest sales?',
                              'What is the peak purchasing time?',
                              'What is the demand for each product?',
                              'Sales trend analysis'))

st.sidebar.markdown('''
### Developed by
[Mugumya Twarik Harouna](https://www.linkedin.com/in/twarik/)

Source code available [here](https://github.com/twarik/Sales-Data-Analysis)''')

#----------------1. What were the best and worst months for sales?------------------
if status == 'What were the best and worst months for sales?':
    grouped_months = data.groupby(by=["month"]).sum()
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']
    grouped_months.reset_index(inplace=True)
    grouped_months.month = months
    source = ColumnDataSource(grouped_months)

    st.markdown('''
    ## What was the best/worst month for sales?
    ### How much was earned that month?
    ''')

    p = create_figure(TOOLS=TOOLS,x_label='Months',y_label='Sales in USD ($)',height=400,x_ticks=months)

    p.vbar(x='month', top='Sales', width=0.9, source=source,
       fill_color=factor_cmap('month', palette=Paired12[::-1], factors=grouped_months['month']))

    h = hover([('Month', "@month"), ('Sales', "$@Sales")])
    p.add_tools(h)
    st.bokeh_chart(p, use_container_width=True)

#-------2. Which cities had the highest and lowest sales?--------------------
elif status == 'Which cities had the highest and lowest sales?':
    group_city = data.groupby(by=["City"]).sum()
    group_city.reset_index(inplace=True)
    source = ColumnDataSource(group_city)

    st.markdown(
    '''
    ## Which cities had the highest and lowest sales?
    ### How much was earned from every city?
    '''
    )

    p = create_figure(TOOLS=TOOLS,x_label='Cities',y_label='Sales in USD ($)',height=400,x_ticks=group_city['City'])
    p.vbar(x='City', top='Sales', width=0.9, source=source, fill_color=factor_cmap('City', palette=Paired12, factors=group_city['City']))

    h = hover([('City', "@City"),('Sales', "$@Sales")])
    p.add_tools(h)
    p.xaxis.major_label_orientation = "vertical"
    st.bokeh_chart(p, use_container_width=True)

#-------------------3. What is the peak purchasing time?-----------------------
elif status == 'What is the peak purchasing time?':
    group_hour = data.groupby(by=["hour"]).count()
    group_hour.reset_index(inplace=True)
    source = ColumnDataSource(group_hour)

    '## What is the peak purchasing time?'

    p = create_figure(TOOLS=TOOLS,title='Daily purchase profile',x_label='Hours',y_label='No. of transactions',height=400,x_type='linear')
    p.circle(x='hour', y='Sales', radius=0.15, fill_color='green', source=source)
    p.line(x='hour', y='Sales', line_width=2.5, line_color='red', source=source)

    h = hover([('Transactions', "@Sales"), ('Hour', "@hour")])
    p.add_tools(h)
    st.bokeh_chart(p, use_container_width=True)

    t = group_hour.Sales.idxmax()
    'The peak purchasing time is %sh' %t

#--------------4. What is the demand for each product?--------------------------
elif status == 'What is the demand for each product?':
    group_product = data.groupby(by=["Product"]).count()
    group_product.reset_index(inplace=True)
    group_product['radius'] = group_product['Sales']/group_product['Sales'].max()
    products = group_product['Product'].tolist()
    source = ColumnDataSource(group_product)

    '## What is the demand for each product?'

    p = create_figure(TOOLS=TOOLS,x_label='Product',y_label='Products sold annually',height=500,x_ticks=products)

    p.asterisk(x='Product', y='Sales', fill_color='black', source=source)
    p.circle(x='Product', y='Sales', radius='radius', line_color='grey', source=source,
            fill_color=factor_cmap('Product', palette=Category20_20[:len(products)], factors=products), alpha=0.7)

    h = hover([('Product name', "@Product"), ('# Units sold', "@Sales")])
    p.add_tools(h)
    p.xaxis.major_label_orientation = "vertical"
    st.bokeh_chart(p, use_container_width=True)

#------------------------5. 'Sales trend analysis'---------------------------
elif status == 'Sales trend analysis':
    group_product = data.groupby(by=["Product"]).count()
    group_product.reset_index(inplace=True)
    products = group_product['Product'].tolist()

    '## Sales trend analysis by product'
    multi_prod = st.multiselect('Type/select product/s for trend analysis', (products))

    p = create_figure(TOOLS=TOOLS,x_label='Date',y_label='Daily sales',height=300,x_type='datetime')

    for idx, val in enumerate(multi_prod):
        product_df = data.loc[data['Product'] == val]
        product_df=product_df.groupby(by=["Date"]).sum()
        product_df.reset_index(inplace=True)
        source = ColumnDataSource(product_df)
        p.line(x='Date', y='Sales', legend_label=val, line_color=Category20_20[idx], source=source)

    h = hover([('', "$@Sales")])
    p.add_tools(h)
    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    if len(multi_prod) !=0:
        p.add_layout(p.legend[0], 'right')
    st.bokeh_chart(p, use_container_width=True)

else:
    st.title("Analysis of sales data")

    daily=data.groupby(by=["Date"]).sum()
    daily.reset_index(inplace=True)
    source = ColumnDataSource(daily)

    '#### Time series of the sales made on a daily basis during 2019'

    p = create_figure(TOOLS=TOOLS,x_label='Date',y_label='Sales',height=300,x_type='datetime')

    p.line(x='Date', y='Sales', source=source)

    h = hover([('Sales', "$@Sales")])
    p.add_tools(h)
    p.y_range.start = 350
    st.bokeh_chart(p, use_container_width=True)

    if st.checkbox('View table'):
        '#### Table below shows a sample of the sales data'
        variables = ['Product', 'Quantity Ordered', 'Price Each', 'Order Date', 'City']
        st.dataframe(data[variables].rename(columns={"Quantity Ordered": "Qty", "Price Each": "Price"}).sample(100))

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

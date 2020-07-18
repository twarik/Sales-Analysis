#Import necesssay libraries
import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Paired12, Category20_20
from bokeh.transform import factor_cmap

import warnings
warnings.filterwarnings('ignore')

st.sidebar.markdown('''# Sales Analysis''')

#Read in dataset
@st.cache(allow_output_mutation=True)
def load_data():
    return pd.read_csv('./sales_data.csv')

data = load_data()

#Define tools to add on the plots
TOOLS = 'pan,zoom_out,box_zoom,reset,save'
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
    grouped_months = data.groupby('month').sum()
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']
    grouped_months.reset_index(inplace=True)
    grouped_months.month = months

    st.markdown('''
    ## What was the best/worst month for sales?
    ### How much was earned that month?
    ''')
    source = ColumnDataSource(grouped_months)

    p = figure(tools = TOOLS,
        x_axis_label='Months',
        y_axis_label='Sales in USD ($)',
        height=400,
        x_range=months
        )

    p.vbar(x='month', top='Sales', width=0.9, source=source,
       fill_color=factor_cmap('month', palette=Paired12[::-1], factors=grouped_months['month']))

    hover = HoverTool()
    hover.tooltips=[
        ('Month', "@month"),
        ('Sales', "$@Sales"),
    ]
    p.add_tools(hover)
    st.bokeh_chart(p, use_container_width=True)

#-------2. Which cities had the highest and lowest sales?--------------------
elif status == 'Which cities had the highest and lowest sales?':
    group_city = data.groupby('City').sum()
    group_city.reset_index(inplace=True)

    st.markdown(
    '''
    ## Which cities had the highest and lowest sales?
    ### How much was earned from every city?
    '''
    )
    source = ColumnDataSource(group_city)

    p = figure(tools = TOOLS,
        x_axis_label='Cities',
        y_axis_label='Sales in USD ($)',
        height=400,
        x_range=group_city['City']
        )

    p.vbar(x='City', top='Sales', width=0.9, source=source,
       fill_color=factor_cmap('City', palette=Paired12, factors=group_city['City']))

    hover = HoverTool()
    hover.tooltips=[
        ('City', "@City"),
        ('Sales', "$@Sales"),
    ]
    p.add_tools(hover)
    p.xaxis.major_label_orientation = "vertical"

    st.bokeh_chart(p, use_container_width=True)

#-------------------3. What is the peak purchasing time?-----------------------
elif status == 'What is the peak purchasing time?':
    group_hour = data.groupby('hour').count()
    group_hour.reset_index(inplace=True)
    source = ColumnDataSource(group_hour)

    '## What is the peak purchasing time?'

    p = figure(tools = TOOLS,
        title='Daily purchase profile',
        x_axis_label='Hours',
        y_axis_label='No. of transactions',
        height=400,
        )

    p.circle(x='hour', y='Sales', radius=0.15, fill_color='green', source=source)
    p.line(x='hour', y='Sales', line_width=2.5, line_color='red', source=source)

    hover = HoverTool()
    hover.tooltips=[
        ('Transactions', "@Sales"),
        ('Hour', "@hour"),
    ]
    p.add_tools(hover)

    st.bokeh_chart(p, use_container_width=True)

    t = group_hour.Sales.idxmax()

    'The peak purchasing time is %sh' %t

#--------------4. What is the demand for each product?--------------------------
elif status == 'What is the demand for each product?':
    group_product = data.groupby('Product').count()
    group_product.reset_index(inplace=True)
    group_product['radius'] = group_product['Sales']/group_product['Sales'].max()
    products = group_product['Product'].tolist()

    source = ColumnDataSource(group_product)

    '## What is the demand for each product?'

    p = figure(tools = TOOLS,
        x_axis_label='Product',
        y_axis_label='Products sold annually',
        height=500,
        x_range=products,
        )

    p.asterisk(x='Product', y='Sales', fill_color='black', source=source)
    p.circle(x='Product', y='Sales', radius='radius', line_color='grey', source=source,
            fill_color=factor_cmap('Product', palette=Category20_20[:len(products)], factors=products), alpha=0.7)

    hover = HoverTool()
    hover.tooltips=[
        ('Product', "@Product"),
        ('No. of products sold', "@Sales"),
    ]
    p.add_tools(hover)
    p.xaxis.major_label_orientation = "vertical"
    st.bokeh_chart(p, use_container_width=True)

#------------------------5. 'Sales trend analysis'---------------------------
elif status == 'Sales trend analysis':
    group_product = data.groupby('Product').count()
    group_product.reset_index(inplace=True)
    products = group_product['Product'].tolist()

    source = ColumnDataSource(group_product)

    '## Sales trend analysis by product'

    multi_prod = st.multiselect('Type/select product(s) for trend analysis', (products))

    p = figure(tools = TOOLS,
        x_axis_label='Date',
        y_axis_label='Sales',
        height=300,
        x_axis_type='datetime')

    for idx, val in enumerate(multi_prod):
        product_df = data.loc[data['Product'] == val]
        product_df=product_df.groupby('Date').sum()
        product_df.reset_index(inplace=True)

        source = ColumnDataSource(product_df)

        p.line(x='Date', y='Sales', legend_label=val, line_color=Category20_20[idx], source=source)

    hover = HoverTool()
    hover.tooltips=[
        ('', "$@Sales"),
    ]
    p.add_tools(hover)

    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    if len(multi_prod) !=0:
        p.add_layout(p.legend[0], 'right')

    st.bokeh_chart(p, use_container_width=True)

else:
    st.title("Analysis of sales data")

    daily=data.groupby('Date').sum()
    daily.reset_index(inplace=True)

    '#### Time series of the sales made on a daily basis during 2019'
    source = ColumnDataSource(daily)

    p = figure(tools = TOOLS,
        x_axis_label='Date',
        y_axis_label='Sales',
        height=300,
        x_axis_type='datetime')

    p.line(x='Date', y='Sales', source=source)

    hover = HoverTool()
    hover.tooltips=[
        ('Sales', "$@Sales"),
    ]
    p.add_tools(hover)
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

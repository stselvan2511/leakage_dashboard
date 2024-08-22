import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    return pd.read_excel(r'data/NRW_dataset6.xlsx')

df = load_data()

# Streamlit dashboard
st.title('Water Consumption Dashboard')

# Sidebar filters
st.sidebar.header('Filters')
selected_users = st.sidebar.multiselect('Select User IDs', options=df['User_ID'].unique())
selected_area_codes = st.sidebar.multiselect('Select Area Codes', options=df['Area_Code'].unique())
selected_devices = st.sidebar.multiselect('Select Device IDs', options=df['Device_ID'].unique())
selected_weather = st.sidebar.multiselect('Select Weather Conditions', options=df['Weather_Condition'].unique())

if selected_users:
    df = df[df['User_ID'].isin(selected_users)]
if selected_area_codes:
    df = df[df['Area_Code'].isin(selected_area_codes)]
if selected_devices:
    df = df[df['Device_ID'].isin(selected_devices)]
if selected_weather:
    df = df[df['Weather_Condition'].isin(selected_weather)]

# Plotting Monthly Water Consumption
st.subheader('Monthly Water Consumption by Area Code')
monthly_consumption = df.groupby(['Year', 'Month', 'Area_Code'])['Hourly_Water_Consumption'].sum().reset_index()
monthly_consumption['Date'] = pd.to_datetime(monthly_consumption[['Year', 'Month']].assign(DAY=1))
fig_monthly = px.line(monthly_consumption, x='Date', y='Hourly_Water_Consumption', color='Area_Code',
                      title='Monthly Water Consumption by Area Code')
st.plotly_chart(fig_monthly)

# Plotting Yearly Water Consumption by Area Code
st.subheader('Yearly Water Consumption by Area Code')
yearly_consumption = df.groupby(['Year', 'Area_Code'])['Hourly_Water_Consumption'].sum().reset_index()
fig_yearly = px.bar(yearly_consumption, x='Year', y='Hourly_Water_Consumption', color='Area_Code', 
                    title='Yearly Water Consumption by Area Code', text='Hourly_Water_Consumption',
                    labels={'Hourly_Water_Consumption': 'Water Consumption (liters)'})
st.plotly_chart(fig_yearly)

# Plotting Monthly Leakage Over Time
st.subheader('Monthly Leakage Over Time')
leakage_values = [
    762.163647, 758.553625, 689.222046, 821.455567,
    749.942076, 574.806347, 810.309899, 749.786654,
    761.335840, 748.336110, 748.391032, 697.721186
]
dates = [datetime(2023, i+1, 1) for i in range(12)]
leakage_data = pd.DataFrame({
    'Date': dates,
    'Leakage': leakage_values
})
fig_leakage = px.line(leakage_data, x='Date', y='Leakage', title='Monthly Leakage Over Time',
                      labels={'Leakage': 'Leakage (liters)'})
st.plotly_chart(fig_leakage)

# Plotting Area Tank Level Over Time
st.subheader('Area Tank Level Over Time')
area_tank_level_data = df.groupby(['Year', 'Month', 'Area_Code'])['Area_Tank_Level'].mean().reset_index()
area_tank_level_data['Date'] = pd.to_datetime(area_tank_level_data[['Year', 'Month']].assign(DAY=1))
fig_area_tank_level = px.line(area_tank_level_data, x='Date', y='Area_Tank_Level', color='Area_Code',
                              title='Average Area Tank Level Over Time')
st.plotly_chart(fig_area_tank_level)

# Plotting Weather Conditions Impact
st.subheader('Impact of Weather Conditions on Water Consumption')
weather_impact = df.groupby(['Year', 'Month', 'Weather_Condition'])['Hourly_Water_Consumption'].mean().reset_index()
weather_impact['Date'] = pd.to_datetime(weather_impact[['Year', 'Month']].assign(DAY=1))
fig_weather = px.line(weather_impact, x='Date', y='Hourly_Water_Consumption', color='Weather_Condition',
                      title='Impact of Weather Conditions on Water Consumption')
st.plotly_chart(fig_weather)

# Plotting Main and Area Tank Levels
st.subheader('Main and Area Tank Levels')
tank_levels = df.groupby(['Year', 'Month'])[['Main_Tank_Level', 'Area_Tank_Level']].mean().reset_index()
tank_levels['Date'] = pd.to_datetime(tank_levels[['Year', 'Month']].assign(DAY=1))
fig_tank_levels = px.line(tank_levels, x='Date', y=['Main_Tank_Level', 'Area_Tank_Level'], 
                          title='Main and Area Tank Levels Over Time')
st.plotly_chart(fig_tank_levels)

# Plotting Pressure Data Over Time
st.subheader('Pressure Data Over Time')
pressure_cols = ['Main_Tank_Pressure', 'Area_Pressure', 'User_Pressure']
if all(col in df.columns for col in pressure_cols):
    pressure_data = df.groupby(['Year', 'Month'])[pressure_cols].mean().reset_index()
    pressure_data['Date'] = pd.to_datetime(pressure_data[['Year', 'Month']].assign(DAY=1))
    fig_pressure = px.line(pressure_data, x='Date', y=pressure_cols, 
                           title='Pressure Data Over Time', labels={'value': 'Pressure (bars)'})
    st.plotly_chart(fig_pressure)
else:
    st.warning('Pressure data columns not found. Please check your dataset.')

# Create a flowchart with Graphviz
st.subheader('Water Distribution Flowchart')
dot = graphviz.Digraph(comment='Water Distribution Network', format='png')
dot.attr(rankdir='LR')

# Define nodes for the Water Tank and Main Device
dot.node('Tank', 'Water Tank\nCapacity: 100,000 liters\nAlert Levels: 25%, 50%, 75%, 100%', shape='box', style='filled', color='lightblue')
dot.node('MainDevice', 'Main Device\nDevice ID: Main_Device', shape='box', style='filled', color='lightgrey')

# Define nodes for the Area Devices
for i in range(1, 5):
    dot.node(f'AreaDevice{i}', f'Area Device {i}\nConnected Pipeline {i}', shape='box', style='filled', color='purple')

# Define nodes for the Areas
for i in range(1, 5):
    dot.node(f'Area{i}', f'Area {i}\nPopulation: {100 + i * 50}', shape='ellipse', style='filled', color='yellow')

# Define nodes for the Users and their Devices
for i in range(1, 13):
    dot.node(f'User{i}', f'User {i}\nUsage: {100 + i * 10} liters/day', shape='ellipse')
    dot.node(f'Device{i}', f'Device {i}\nID: Device_{i}', shape='box', style='filled', color='lightpink')

# Create edges to represent the water flow
dot.edge('Tank', 'MainDevice', label='Water Supply\nTotal: 100,000 liters/day')

for i in range(1, 5):
    dot.edge('MainDevice', f'AreaDevice{i}', label=f'Pipeline {i}')
    dot.edge(f'AreaDevice{i}', f'Area{i}', label=f'To Area {i}')

# Connect Areas to Users
for i in range(1, 13):
    area_id = (i - 1) // 3 + 1  # Determine area based on user index
    dot.edge(f'Area{area_id}', f'User{i}', label=f'Supply to User {i}')
    dot.edge(f'User{i}', f'Device{i}', label=f'Connected to Device {i}')

# Render and display the flowchart
st.graphviz_chart(dot)

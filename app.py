import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Load the data directly from your course URL
df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# 2. App Layout
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", 
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}),
    
    # Dropdown for Report Type
    html.Div([
        html.Label("Select Report Type:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Automobile Sales Statistics', 'value': 'Yearly Status'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Status'}
            ],
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),
    
    # Dropdown for Year Selection
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in range(1980, 2014)],
            placeholder='Select Year',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),
    
    # Container where the graphs will be rendered dynamically
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flex-wrap': 'wrap'}),
    ])
])

# 3. Callback to disable the Year dropdown when "Recession" is selected
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Recession Status': 
        return True
    else: 
        return False

# 4. Callback to render the main statistical graphs
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(report_type, input_year):
    if not report_type:
        return None

    # ================= RECESSION PERIOD STATISTICS =================
    if report_type == 'Recession Status':
        # Filter for rows where Recession equals 1
        recession_data = df[df['Recession'] == 1]
        
        # Chart 1: Average Automobile Sales Fluctuation Over Recession Period
        sales_by_year = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(sales_by_year, x='Year', y='Automobile_Sales', 
                                            title="Average Automobile Sales Over Recession Period"))
        
        # Chart 2: Average Number of Vehicles Sold by Vehicle Type
        avg_vehicles = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(avg_vehicles, x='Vehicle_Type', y='Automobile_Sales', 
                                           title="Avg Vehicles Sold by Type During Recessions"))
        
        # Chart 3: Total Expenditure Share by Vehicle Type During Recessions
        exp_share = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_share, values='Advertising_Expenditure', names='Vehicle_Type', 
                                           title="Advertising Expenditure Share During Recessions"))
        
        # Chart 4: Effect of Unemployment Rate on Vehicle Type and Sales
        unemp_chart = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_chart, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                                           title="Effect of Unemployment Rate on Sales by Vehicle Type"))
        
        # Group into rows of side-by-side graphs
        return [
            html.Div([R_chart1, R_chart2], style={'display': 'flex', 'width': '100%'}),
            html.Div([R_chart3, R_chart4], style={'display': 'flex', 'width': '100%'})
        ]

    # ================= YEARLY AUTOMOBILE SALES STATISTICS =================
    elif report_type == 'Yearly Status' and input_year:
        # Filter data for the specific chosen year
        yearly_data = df[df['Year'] == int(input_year)]
        
        # Chart 1: Yearly Automobile Sales Using Line Chart for the Whole Period
        all_years = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(all_years, x='Year', y='Automobile_Sales', 
                                            title="Grand Trend: Average Yearly Automobile Sales"))
        
        # Chart 2: Total Monthly Automobile Sales for the Selected Year
        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(monthly_sales, x='Month', y='Automobile_Sales', 
                                            title=f"Total Monthly Sales in {input_year}"))
        
        # Chart 3: Average Vehicles Sold by Vehicle Type in the Selected Year
        avg_v_type = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avg_v_type, x='Vehicle_Type', y='Automobile_Sales', 
                                           title=f"Avg Vehicles Sold by Type in {input_year}"))
        
        # Chart 4: Total Advertisement Expenditure for Each Vehicle Using Pie Chart
        total_exp = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(total_exp, values='Advertising_Expenditure', names='Vehicle_Type', 
                                           title=f"Advertising Expenditure Share in {input_year}"))
        
        # Group into rows of side-by-side graphs
        return [
            html.Div([Y_chart1, Y_chart2], style={'display': 'flex', 'width': '100%'}),
            html.Div([Y_chart3, Y_chart4], style={'display': 'flex', 'width': '100%'})
        ]
    
    return None

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
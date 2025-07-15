from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from htmltools import css
from shinywidgets import output_widget, render_widget
import os

# Read the CSV file
def load_data(file_path=None):
    if file_path is not None:
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return None, f"Error loading file: {str(e)}"
    else:
        default_path = "data/w771dz_sangamura_20240901-20240930.csv"
        if not os.path.exists(default_path):
            return None, f"Default data file not found at {default_path}"
        df = pd.read_csv(default_path)
    
    try:
        if 'date' in df.columns and 'time' in df.columns:
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y/%m/%d %H:%M')
        elif 'datetime' not in df.columns:
            return None, "CSV must have either 'datetime' column or 'date' and 'time' columns"
            
        df = df.replace('', np.nan)
        
        numeric_cols = ['temperature', 'humidity', 'light', 'rainfall_5min', 
                       'rainfall_1hour', 'wind_speed', 'atmospheric_pressure']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

# Define UI
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.title("│ Sangamura Farm Weather Dashboard"),  # Set the browser tab title
    ),
    ui.tags.style("""
        .value-box {
            border-radius: 10px;
            padding: 15px;
            margin: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            min-height: 100px;
        }
        .value-title {
            font-size: 16px;
            margin-bottom: 10px;
        }
        .value-content {
            font-size: 24px;
            font-weight: bold;
        }
        .temp-box { background-color: rgba(255, 99, 132, 0.7); }
        .humid-box { background-color: rgba(54, 162, 235, 0.7); }
        .light-box { background-color: rgba(255, 206, 86, 0.7); }
        .rain-box { background-color: rgba(75, 192, 192, 0.7); }
        .wind-box { background-color: rgba(153, 102, 255, 0.7); }
        .pressure-box { background-color: rgba(255, 159, 64, 0.7); }
        .wind-dir-box { background-color: rgba(199, 199, 199, 0.7); }
    """),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("三ヶ村天気予報ダッシュボード Sangamura Weather Dashboard"),
            # ui.input_slider(
            #     "datetime_slider",
            #     "Select Date/Time:",
            #     min=0,
            #     max=len(df) - 1,
            #     value=0,
            #     step=1
            # ),
            ui.div(
                {"class": "upload-container"},
                ui.input_file("csv_file", "Data source:", accept=".csv"),
                ui.output_ui("data_status")
            ),
            ui.input_date(
                "selected_date",
                "Select Date:",
                value = None, # df['datetime'].dt.date.min(),
                min = None, # df['datetime'].dt.date.min(),
                max = None # df['datetime'].dt.date.max(),
            ),
            ui.input_select(
                "selected_time",
                "Select Time:",
                choices = [], # [t.strftime('%H:%M') for t in sorted(df['datetime'].dt.time.unique())],
                selected = None # df['datetime'].dt.time.min().strftime('%H:%M')
            ),
            ui.output_text("selected_datetime"),
            width="300px"
        ),
        ui.navset_tab(
            ui.nav_panel(
                "About",
                ui.div(
                    {"class": "about-container"},
                    ui.h2("三ヶ村農場 │ Sangamura Farm"),
                    ui.img({"src": "https://github.com/Rau-KaTRI/SangamuraPics/blob/main/DNC_3149.JPG?raw=true", 
                            "alt": "Sangamura Farm Weather Station", 
                            "class": "about-image"}),
                    ui.p("""

                    """),  
                    ui.p("""
                        三ヶ村農場気象ダッシュボードは、当農場の気象観測所から収集されたリアルタイムおよび過去の気象データを提供します。
                        この観測所は新潟県十日町市に位置し、気温、湿度、降雨量、風のパターン、大気圧などの環境パラメーターを監視しています。
                        The Sangamura Farm Weather Dashboard provides real-time and historical weather data 
                        collected from our on-site weather station. Located in Tokamachi City, Niigata Prefecture, 
                        this station monitors environmental parameters including temperature, humidity, rainfall, 
                        wind patterns, and atmospheric pressure.
                    """),                 
                    ui.p("""
                        これらのデータは、地元の農家が灌漑スケジュールを最適化し、収穫活動を計画し、悪天候時の保護対策を実施するのに役立つと期待されています。
                        観測所にはセンサーが設置されており、日々の測定値を記録し、農業地帯における微気候のパターンに関する洞察を提供します。These data are expected to help local farmers optimize irrigation schedules, plan harvesting activities, 
                        and implement protective measures during adverse weather conditions. The station is 
                        equipped with sensors that record daily measurements, providing 
                        insights into microclimate patterns across the agricultural landscape.
                    """)
                )
            ),
            ui.nav_panel(
                "All",
                ui.output_ui("value_boxes"),
                ui.h4("Current Weather Status"),
                ui.div(
                    {"class": "row"},
                    ui.div(
                        {"class": "col-md-6"},
                        output_widget("temperature_gauge")
                    ),
                    ui.div(
                        {"class": "col-md-6"},
                        output_widget("humidity_gauge")
                    )
                ),
                ui.div(
                    {"class": "row mt-3"},
                    ui.div(
                        {"class": "col-md-6"},
                        output_widget("wind_rose")
                    ),
                    ui.div(
                        {"class": "col-md-6"},
                        output_widget("pressure_gauge")
                    )
                )
            ),
            ui.nav_panel(
                "Temperature",
                output_widget("temperature_plot")
            ),
            ui.nav_panel(
                "Rainfall",
                output_widget("rainfall_plot")
            ),
            ui.nav_panel(
                "Humidity",
                output_widget("humidity_plot")
            ),
            ui.nav_panel(
                "Light",
                output_widget("light_plot")
            ),
            ui.nav_panel(
                "Atmospheric Pressure",
                output_widget("pressure_plot")
            ),
            ui.nav_panel(
                "Wind",
                output_widget("wind_plot")
            )
        )
    )
)

# Define server
def server(input, output, session):
    rv = reactive.Value(None)
    error_msg = reactive.Value(None)

    # Initial data load
    df_init, init_error = load_data()
    if df_init is not None:
        rv.set(df_init)
    else:
        error_msg.set(init_error)

    @reactive.Effect
    @reactive.event(input.csv_file)
    def _():
        # Reset error message
        error_msg.set(None)
        
        # Get uploaded file
        file_info = input.csv_file()
        
        if file_info and file_info[0] is not None:
            # Load data from uploaded file
            df_new, new_error = load_data(file_info[0]['datapath'])
            if df_new is not None:
                rv.set(df_new)
                
                # Update date input
                min_date = df_new['datetime'].dt.date.min()
                max_date = df_new['datetime'].dt.date.max()
                ui.update_date(
                    "selected_date",
                    value = min_date,
                    min = min_date,
                    max = max_date
                )
                
                # Update time input
                new_times = [t.strftime('%H:%M') for t in sorted(df_new['datetime'].dt.time.unique())]
                ui.update_select(
                    "selected_time",
                    choices = new_times,
                    selected = new_times[0] if new_times else None
                )
            else:
                error_msg.set(new_error)

    # Initialize UI date and time selectors
    @reactive.Effect
    def _():
        df = rv.get()
        if df is not None:
            # Update date input
            min_date = df['datetime'].dt.date.min()
            max_date = df['datetime'].dt.date.max()
            ui.update_date(
                "selected_date",
                value = min_date,
                min = min_date,
                max = max_date
            )
            
            # Update time input
            times = [t.strftime('%H:%M') for t in sorted(df['datetime'].dt.time.unique())]
            ui.update_select(
                "selected_time",
                choices = times,
                selected = times[0] if times else None
            )

    @output
    @render.ui
    def data_status():
        error = error_msg.get()
        
        if error:
            return ui.div(
                {"class": "error-message"},
                error
            )
        elif rv.get() is not None:
            source = "Uploaded file" if input.file_upload() else "Default data"
            return ui.div(
                {"class": "success-message"},
                f"Data loaded successfully from {source}"
            )
        else:
            return ui.div(
                {"class": "error-message"},
                "No data available"
            )

    @reactive.Calc
    def selected_index():
        df = rv.get()
        if df is None:
            return 0
        
        selected_date = input.selected_date()
        selected_time = input.selected_time()
        
        if selected_date is None or selected_time is None:
            return 0

        datetime_str = f"{selected_date} {selected_time}"
        try:
            target_datetime = pd.to_datetime(datetime_str)
            return df['datetime'].sub(target_datetime).abs().idxmin()
        except:
            return 0

    @output
    @render.text
    def selected_datetime():
        df = rv.get()
        if df is None:
            return "No data available"
        
        # idx = input.datetime_slider()
        idx = selected_index()
        return f"Selected: {df.iloc[idx]['datetime'].strftime('%Y-%m-%d %H:%M')}"
    
    @output
    @render.ui
    def value_boxes():
        df = rv.get()
        if df is None:
            return ui.p("No data available")

        # idx = input.datetime_slider()
        idx = selected_index()
        selected_data = df.iloc[idx]
        
        temperature = selected_data['temperature'] if not pd.isna(selected_data['temperature']) else "N/A"
        humidity = selected_data['humidity'] if not pd.isna(selected_data['humidity']) else "N/A"
        light = selected_data['light'] if not pd.isna(selected_data['light']) else "N/A"
        rainfall_5min = selected_data['rainfall_5min'] if not pd.isna(selected_data['rainfall_5min']) else "N/A"
        rainfall_1hour = selected_data['rainfall_1hour'] if not pd.isna(selected_data['rainfall_1hour']) else "N/A"
        wind_speed = selected_data['wind_speed'] if not pd.isna(selected_data['wind_speed']) else "N/A"
        wind_direction = selected_data['wind_direction'] if not pd.isna(selected_data['wind_direction']) else "N/A"
        pressure = selected_data['atmospheric_pressure'] if not pd.isna(selected_data['atmospheric_pressure']) else "N/A"
        
        return ui.div(
            {"class": "row"},
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box temp-box"},
                    ui.div({"class": "value-title"}, "Temperature"),
                    ui.div({"class": "value-content"}, f"{temperature} °C")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box humid-box"},
                    ui.div({"class": "value-title"}, "Humidity"),
                    ui.div({"class": "value-content"}, f"{humidity} %")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box light-box"},
                    ui.div({"class": "value-title"}, "Light"),
                    ui.div({"class": "value-content"}, f"{light}")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box rain-box"},
                    ui.div({"class": "value-title"}, "Rainfall (5 min)"),
                    ui.div({"class": "value-content"}, f"{rainfall_5min} mm")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box rain-box"},
                    ui.div({"class": "value-title"}, "Rainfall (1 hour)"),
                    ui.div({"class": "value-content"}, f"{rainfall_1hour} mm")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box wind-box"},
                    ui.div({"class": "value-title"}, "Wind Speed"),
                    ui.div({"class": "value-content"}, f"{wind_speed} m/s")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box wind-dir-box"},
                    ui.div({"class": "value-title"}, "Wind Direction"),
                    ui.div({"class": "value-content"}, f"{wind_direction}")
                )
            ),
            ui.div(
                {"class": "col-md-3"},
                ui.div(
                    {"class": "value-box pressure-box"},
                    ui.div({"class": "value-title"}, "Pressure"),
                    ui.div({"class": "value-content"}, f"{pressure} hPa")
                )
            )
        )
    
    # Temperature plot
    @render_widget
    def temperature_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        fig = px.line(
            df, 
            x='datetime', 
            y='temperature',
            title='Temperature Over Time',
            labels={'temperature': 'Temperature (°C)', 'datetime': 'Date & Time'},
            template='plotly_dark'
        )
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_temp = df.iloc[idx]['temperature']
        
        if not pd.isna(selected_temp):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_temp],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
        return fig
    
    # Rainfall plot
    @render_widget
    def rainfall_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        fig = px.line(
            df, 
            x='datetime', 
            y='rainfall_1hour',
            title='Rainfall (1 hour) Over Time',
            labels={'rainfall_1hour': 'Rainfall (mm)', 'datetime': 'Date & Time'},
            template='plotly_dark'
        )
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_rain = df.iloc[idx]['rainfall_1hour']
        
        if not pd.isna(selected_rain):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_rain],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
        return fig
    
    # Humidity plot
    @render_widget
    def humidity_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")
        
        fig = px.line(
            df, 
            x='datetime', 
            y='humidity',
            title='Humidity Over Time',
            labels={'humidity': 'Humidity (%)', 'datetime': 'Date & Time'},
            template='plotly_dark'
        )
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_humidity = df.iloc[idx]['humidity']
        
        if not pd.isna(selected_humidity):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_humidity],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
        return fig
    
    # Light plot
    @render_widget
    def light_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        fig = px.line(
            df, 
            x='datetime', 
            y='light',
            title='Light Intensity Over Time',
            labels={'light': 'Light Intensity', 'datetime': 'Date & Time'},
            template='plotly_dark'
        )
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_light = df.iloc[idx]['light']
        
        if not pd.isna(selected_light):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_light],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
        return fig
    
    # Pressure plot
    @render_widget
    def pressure_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        fig = px.line(
            df, 
            x='datetime', 
            y='atmospheric_pressure',
            title='Atmospheric Pressure Over Time',
            labels={'atmospheric_pressure': 'Pressure (hPa)', 'datetime': 'Date & Time'},
            template='plotly_dark'
        )
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_pressure = df.iloc[idx]['atmospheric_pressure']
        
        if not pd.isna(selected_pressure):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_pressure],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
        return fig
    
    # Wind plot
    @render_widget
    def wind_plot():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")
        
        fig = go.Figure()
        
        # Add wind speed line
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['wind_speed'],
                mode='lines',
                name='Wind Speed (m/s)',
                line=dict(color='blue')
            )
        )
        
        # Add annotations for wind direction at regular intervals
        step = max(1, len(df) // 20)  # Show about 20 directions on the plot
        for i in range(0, len(df), step):
            if not pd.isna(df.iloc[i]['wind_direction']):
                fig.add_annotation(
                    x=df.iloc[i]['datetime'],
                    y=df.iloc[i]['wind_speed'] if not pd.isna(df.iloc[i]['wind_speed']) else 0,
                    text=df.iloc[i]['wind_direction'],
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-30
                )
        
        # Add marker for selected point
        # idx = input.datetime_slider()
        idx = selected_index()
        selected_time = df.iloc[idx]['datetime']
        selected_speed = df.iloc[idx]['wind_speed']
        
        if not pd.isna(selected_speed):
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[selected_speed],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=12
                    ),
                    name='Selected'
                )
            )
            
            if not pd.isna(df.iloc[idx]['wind_direction']):
                fig.add_annotation(
                    x=selected_time,
                    y=selected_speed,
                    text=df.iloc[idx]['wind_direction'],
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    font=dict(size=14, color="red")
                )
        
        fig.update_layout(
            title='Wind Speed and Direction Over Time',
            xaxis_title='Date & Time',
            yaxis_title='Wind Speed (m/s)',
            template='plotly_dark',
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0.1)',
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        return fig
    
    # Gauge for temperature on All tab
    @render_widget
    def temperature_gauge():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        # idx = input.datetime_slider()
        idx = selected_index()
        temp = df.iloc[idx]['temperature']
        
        if pd.isna(temp):
            return go.Figure().update_layout(title="No temperature data available")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=temp,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Temperature (°C)"},
            gauge={
                'axis': {'range': [df['temperature'].min() - 5, df['temperature'].max() + 5]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [df['temperature'].min() - 5, 20], 'color': "blue"},
                    {'range': [20, 25], 'color': "green"},
                    {'range': [25, 30], 'color': "yellow"},
                    {'range': [30, df['temperature'].max() + 5], 'color': "red"},
                ]
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=70, b=20),
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        return fig
    
    # Gauge for humidity on All tab
    @render_widget
    def humidity_gauge():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")
        
        # idx = input.datetime_slider()
        idx = selected_index()
        humidity = df.iloc[idx]['humidity']

        if pd.isna(humidity):
            return go.Figure().update_layout(title="No temperature data available")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=humidity,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Humidity (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range': [0, 30], 'color': "yellow"},
                    {'range': [30, 70], 'color': "green"},
                    {'range': [70, 100], 'color': "orange"},
                ]
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        return fig
    
    # Gauge for pressure on All tab
    @render_widget
    def pressure_gauge():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")
        
        # idx = input.datetime_slider()
        idx = selected_index()
        pressure = df.iloc[idx]['atmospheric_pressure']

        if pd.isna(pressure):
            return go.Figure().update_layout(title="No temperature data available")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pressure,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Pressure (hPa)"},
            gauge={
                'axis': {'range': [df['atmospheric_pressure'].min() - 5, df['atmospheric_pressure'].max() + 5]},
                'bar': {'color': "orange"},
                'steps': [
                    {'range': [df['atmospheric_pressure'].min() - 5, 970], 'color': "red"},
                    {'range': [970, 980], 'color': "yellow"},
                    {'range': [980, df['atmospheric_pressure'].max() + 5], 'color': "green"},
                ]
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=70, b=20),
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        return fig
    
    # Wind rose on All tab
    @render_widget
    def wind_rose():
        df = rv.get()
        if df is None:
            return go.Figure().update_layout(title="No data available")

        # idx = input.datetime_slider()
        idx = selected_index()
        wind_dir = df.iloc[idx]['wind_direction']
        wind_speed = df.iloc[idx]['wind_speed'] if not pd.isna(df.iloc[idx]['wind_speed']) else 0
        
        # Map wind directions to angles
        direction_to_angle = {
            'north': 0,
            'northeast': 45,
            'east': 90,
            'southeast': 135,
            'south': 180,
            'southwest': 225,
            'west': 270,
            'northwest': 315
        }
        
        # Default to north if direction is missing
        angle = direction_to_angle.get(wind_dir.lower() if not pd.isna(wind_dir) else '', 0)
        
        # Create wind rose with arrow pointing in direction wind is coming FROM
        fig = go.Figure()
        
        # Add circular background
        theta = np.linspace(0, 2*np.pi, 100)
        r = np.ones(100)
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=np.degrees(theta),
            mode='lines',
            line=dict(color='rgba(200, 200, 200, 0.2)'),
            showlegend=False
        ))
        
        # Add cardinal directions
        for direction, degrees in direction_to_angle.items():
            fig.add_annotation(
                x=0.5*np.cos(np.radians(degrees)),
                y=0.5*np.sin(np.radians(degrees)),
                text=direction[0].upper(),
                showarrow=False,
                xref="x", yref="y",
                font=dict(size=14, color="white")
            )
        
        # Add arrow for current wind direction (opposite to meteorological direction)
        arrow_angle = (angle + 180) % 360  # Wind direction is where it's coming FROM
        arrow_length = 0.4  # Scale based on wind speed if needed
        
        fig.add_annotation(
            x=arrow_length*np.cos(np.radians(arrow_angle)),
            y=arrow_length*np.sin(np.radians(arrow_angle)),
            ax=0, ay=0,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor="red"
        )
        
        fig.update_layout(
            title=f"Wind: {wind_dir} at {wind_speed} m/s",
            showlegend=False,
            xaxis=dict(
                range=[-0.6, 0.6],
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                range=[-0.6, 0.6],
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            width=300,
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0.1)'
        )
        
        return fig

# Create app
app = App(app_ui, server)
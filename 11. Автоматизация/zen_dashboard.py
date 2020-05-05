#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


db_config = {'user': 'my_user',
             'pwd': 'my_user_password',
             'host': 'localhost',
             'port': 5432,
             'db': 'zen'}
engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                            db_config['pwd'],
                                                            db_config['host'],
                                                            db_config['port'],
                                                            db_config['db']))


query1 = '''
            SELECT * FROM dash_visits
        '''
dash_visits = pd.io.sql.read_sql(query1, con = engine)


query2 = '''
            SELECT * FROM dash_engagement
        '''
dash_engagement = pd.io.sql.read_sql(query2, con = engine)


data_dict = {'dash_visits':dash_visits,'dash_engagement':dash_engagement}

for key, value in data_dict.items():
  data_dict[key]['dt'] = pd.to_datetime(data_dict[key]['dt'], format = '%Y-%m-%d %H:%M:%S')


note = '''
          Анализ пользовательского взаимодействия с карточками статей
       '''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[  
    

    html.H1(children = 'Яндекс.Дзен'),
    html.Br(), 
    html.Label(note),  
    html.Br(),  


    html.Div([         
      html.Div([
        html.Label('С ->'),
            dcc.DatePickerSingle(
                id = 'start-time-date',
                display_format = 'YYYY-MM-DD',
                date = dash_visits['dt'].min()
            ),
            dcc.Input(id = 'start-time-hour',
                      type = 'number',
                      value = dash_visits['dt'].min().hour,
                      step = 1,
                      min = 0,
                      max = 23,
                      className = 'form-contro',
                      ),
            dcc.Input(id = 'start-time-minute',
                      type = 'number',
                      value = dash_visits['dt'].min().minute,
                      step = 1,
                      min = 0,
                      max = 59,
                      className = 'form-contro',
                      ),
 
            html.Label('По ->:'),
            dcc.DatePickerSingle(
                id = 'end-time-date',
                display_format = 'YYYY-MM-DD',
                date = dash_visits['dt'].max()
            ),
            dcc.Input(id = 'end-time-hour',
                      type = 'number',
                      value = dash_visits['dt'].max().hour,
                      step = 1,
                      min = 0,
                      max = 23,
                      className = 'form-contro',
                      ),
            dcc.Input(id = 'end-time-minute',
                      type = 'number',
                      value = dash_visits['dt'].max().minute,
                      step = 1,
                      min = 0,
                      max = 59,
                      className = 'form-contro',
                      ), 


        html.Label('Возрастные группы'),
        dcc.Dropdown(
              options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
              value = dash_visits['age_segment'].unique(), 
              multi = True, 
              id = 'age-dropdown'),

    ], className = 'six columns'),


    html.Div([
        html.Label('Темы карточек'),
        dcc.Dropdown(
              options = [{'label': x, 'value': x} for x in dash_visits['item_topic'].unique()],
              value = dash_visits['item_topic'].unique(), 
              multi = True, 
              id = 'item-topic-dropdown',
              style ={'height':'50%'}),

    ], className = 'six columns'),

    ], className = 'row'),
    html.Br(),

    
    
    html.Div([

    html.Div([
      html.Label('История событий по темам карточек, абсолютные значения'),
      dcc.Graph(
          style = {'height': '50vw'},
          id = 'history-absolute-visits'
        ),

      ],className='six columns'),


    html.Div([
      html.Label('Разбивка событий по темам источников, относительные значения'),
      dcc.Graph(
          style = {'height': '25vw'},
          id = 'pie-visits'
        ),

      ],className='six columns'),


    html.Div([
      html.Label('Средняя глубина взимодействия'),
      dcc.Graph(
          style = {'height': '25vw'}, 
          id = 'engagement-graph'
        ),

      ],className='six columns'),

     

      ],className='row'),
])


@app.callback(
    [Output('history-absolute-visits', 'figure'),
     Output('pie-visits', 'figure'),
     Output('engagement-graph', 'figure'),
    ],
    [
     Input('item-topic-dropdown', 'value'),
     Input('age-dropdown', 'value'),
     Input('start-time-date', 'date'),
     Input('start-time-hour', 'value'),
     Input('start-time-minute', 'value'),
     Input('end-time-date', 'date'),
     Input('end-time-hour', 'value'),
     Input('end-time-minute', 'value'),    
    ])


def update_figures(selected_item_topics, selected_ages, start_time_date, start_time_hour, start_time_minute, end_time_date, end_time_hour, end_time_minute):
  start_date = str(start_time_date) + ' {}:{}'.format(str(start_time_hour).zfill(2), str(start_time_minute).zfill(2))
  end_date = str(end_time_date) + ' {}:{}'.format(str(end_time_hour).zfill(2), str(end_time_minute).zfill(2))


  filtered_dash_data = dash_visits.query('item_topic == @selected_item_topics and \
                                          dt >= @start_date and dt <= @end_date and age_segment == @selected_ages')


  filtered_dash_data_1 = filtered_dash_data.groupby(['item_topic','dt']).agg({'visits':'sum'}).reset_index()

  data_item_topic_dropdown = []
  
  for item in filtered_dash_data['item_topic'].unique():
    current = filtered_dash_data_1[filtered_dash_data_1['item_topic']==item]
    data_item_topic_dropdown += [go.Scatter(x = current['dt'],
                                            y = current['visits'],
                                            mode = 'lines',
                                            stackgroup = 'one',
                                            name = item)
                                ]


  filtered_dash_data_2 = filtered_dash_data.groupby('source_topic').agg({'visits':'sum'}).reset_index()
  
  
  data_pie_source_topic = [go.Pie(labels = filtered_dash_data_2['source_topic'],
                                  values = filtered_dash_data_2['visits'])

                          ]

  
  filtered_dash_data_eng = dash_engagement.query('item_topic == @selected_item_topics and \
                                                   dt >= @start_date and dt <= @end_date \
                                                   and age_segment == @selected_ages')


  filtered_dash_data_3 = filtered_dash_data_eng.groupby('event', as_index=False).agg({'unique_users':'mean'})\
                                                                                .rename(columns = {'unique_users':'avg_unique_users'})\
                                                                                .sort_values('avg_unique_users', ascending = False)

                                                                        
  filtered_dash_data_3['avg_unique_users'] = round((filtered_dash_data_3['avg_unique_users'] / filtered_dash_data_3['avg_unique_users'].max()), 2)                                                                  
  

  data_engagement_graph = [go.Bar( x = filtered_dash_data_3['event'],
                                   y = filtered_dash_data_3['avg_unique_users'],
                                   name = 'Среднее количество пользователей на событие')
                          ]

  

  return (
                #график item-topic-dropdown
            {
                'data': data_item_topic_dropdown,
                'layout': go.Layout(xaxis = {'title': 'Время'},
                                    yaxis = {'title': 'Сумма визитов'})
             },


             {  #график pie-visits
                'data': data_pie_source_topic,
                'layout': go.Layout()

             },


             {
                #график engagement-graph
                'data': data_engagement_graph,
                'layout': go.Layout(xaxis = {'title': 'Тип События'},
                                    yaxis = {'title': 'Среднее число пользователей %'},
                                    hovermode = 'closest')
             },


          )



if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0')

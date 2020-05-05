#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sys



if __name__ == "__main__":
  
  unixOptions = "sdt:edt"
  gnuOptions = ["start_dt=", "end_dt="]
  fullCmdArguments = sys.argv
  argumentList = fullCmdArguments[1:]

  try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
  except getopt.error as err:
    print (str(err))
    sys.exit(2)

  start_dt = ''
  end_dt = ''

  for currentArgument, currentValue in arguments:
    if currentArgument in ("-sdt", "--start_dt"):
      start_dt = currentValue
    elif currentArgument in ("-edt", "--end_dt"):
      end_dt = currentValue


  db_config = {'user':'my_user','pwd':'my_user_password','host':'localhost','port': 5432,'db':'zen'}
  connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
  														   db_config['pwd'],
  														   db_config['host'],
  														   db_config['port'],
  														   db_config['db'])
  engine = create_engine(connection_string)

  # Вы изучили данные в log_raw и выяснили, что в таблице:
  # сохранены события в промежутке между 18:00 и 19:00 24 сентября 2019 года (60 минут);
  # всего 6 возрастных групп;
  # встречаются события 3 типов;
  # есть 25 тем карточек и 26 тем источников.       
  query = ''' SELECT 
                event_id,
                age_segment,
                event,
                item_id,
                item_topic,
                item_type,
                source_id,
                source_topic,
                source_type,
                TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' as dt,
                user_id
            FROM log_raw
            WHERE (TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC') BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
        '''.format(start_dt, end_dt)


  log_raw = pd.io.sql.read_sql(query, con = engine, index_col = 'event_id')
  log_raw['dt'] = pd.to_datetime(log_raw['dt']).dt.round('min')

  
  # Параметры таблицы истории событий: 
  # Тема карточки (item_topic); Тема источника (source_topic); Возрастная категория (age_segment); Дата и время; Количество событий.
  dash_visits = log_raw.groupby(['item_topic', 'source_topic', 'age_segment', 'dt']).agg({'event': 'count'}).rename(columns = {'event': 'visits'}).reset_index()

  
  # Параметры таблицы воронки: 
  # Тема карточки (item_topic); Возрастная категория (age_segment); Дата и время; Тип события (event); Количество уникальных пользователей.
  dash_engagement = log_raw.groupby(['dt', 'item_topic', 'event', 'age_segment']).agg({'user_id': 'nunique'}).rename(columns = {'user_id': 'unique_users'}).reset_index()

  
  tables = {'dash_visits': dash_visits, 'dash_engagement': dash_engagement}
  for table_name, table_data in tables.items():
    query = '''
            DELETE FROM {} WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
          '''.format(table_name, start_dt, end_dt)
    engine.execute(query)
    table_data.to_sql(name = table_name, con = engine, if_exists = 'append', index = False)

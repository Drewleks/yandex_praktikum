1. Создаем ВМ в Яндекс.Облаке.


2. Проверяем подключение
ssh test_admin@84.201.169.172


3. Копируем базу данных, пайплайн и дашборд / :ДВОЕТОЧНИЕ:
scp zen.dump test_admin@84.201.169.172:
scp zen_pipeline.py test_admin@84.201.169.172:
scp zen_dashboard.py test_admin@84.201.169.172:


4. Заходим на ВМ, смотрим есть ли файлы
dir


5. Установим PostgreSQL и обновимся
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt-get install python3-psycopg2


6. Запустим сервер PostgreSQL
sudo service postgresql start
service postgresql status


7. Меняем пользователя на postgres
sudo su postgres


7. Создаем БД
createdb zen --encoding='utf-8'


8. Подключаемся к клиенту СУБД
psql -d zen


9. Проверим таблицы
\dt — пока пусто


8. Создаем пользователя и даем ему права
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE zen TO my_user;


9. Создаем агрегатные таблицы, раздаем права
CREATE TABLE dash_engagement(record_id serial PRIMARY KEY, dt TIMESTAMP, item_topic VARCHAR(128), event VARCHAR(128), age_segment VARCHAR(128), unique_users BIGINT);
GRANT ALL PRIVILEGES ON TABLE dash_engagement TO my_user;
GRANT USAGE, SELECT ON SEQUENCE dash_engagement_record_id_seq TO my_user;

CREATE TABLE dash_visits(record_id serial PRIMARY KEY, item_topic VARCHAR(128), source_topic VARCHAR(128), age_segment VARCHAR(128), dt TIMESTAMP, visits INT);
GRANT ALL PRIVILEGES ON TABLE dash_visits TO my_user;
GRANT USAGE, SELECT ON SEQUENCE dash_visits_record_id_seq TO my_user;


10. Восстановим БД из дампа
pg_restore -d zen zen.dump


11. Вернемся в клиент СУБД
psql -d zen


12. Посмотрим, появились ли таблицы
\dt
SELECT * FROM log_raw LIMIT 50;
\q


13. Установим менеджер пакетов и библиотеки
sudo apt install python3-pip
sudo pip3 install sqlalchemy
sudo pip3 install dash
sudo pip3 install pandas
sudo pip3 install freeze


14. Получим requirements
pip3 freeze


15. Запустим скрипты
python3 zen_pipeline.py --start_dt='2019-09-24 18:00:00' --end_dt='2019-09-24 19:00:00'
python3 zen_dashboard.py


16. Проверим дашборд
http://84.201.169.172:8050/
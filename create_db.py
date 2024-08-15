import sqlite3
from config import config

# Создание или подключение к базе данных
conn = sqlite3.connect(config.path.database)

# Создание курсора
c = conn.cursor()

# Создание таблицы Sales
c.execute('''CREATE TABLE IF NOT EXISTS sales (
    date TEXT,
    sale_id TEXT,
    order_date TEXT,
    order_id TEXT,
    buyer TEXT,
    contractor TEXT,
    site_id TEXT,
    product TEXT,
    feature TEXT,
    quantity INTEGER,
    sum REAL,
    address TEXT,
    cash_flow_type TEXT)''')

# Закрытие соединения с базой данных
conn.close()
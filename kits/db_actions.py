import sqlite3
import pandas as pd

from config import config

# создание базы банных
def crate_db():
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
    
    return None

# добавление строки в таблицу с реализациями
def add_sale(row):
    # Подключение к нашей базе данных
    conn = sqlite3.connect(config.path.database)
    c = conn.cursor()

    c.execute(f'''INSERT INTO sales (
        date, sale_id, order_date, order_id, buyer,
        contractor, site_id, product, feature,
        quantity, sum, address, cash_flow_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (row['date'], row['sale_id'], row['order_date'], row['order_id'], row['buyer'],
         row['contractor'], row['site_id'], row['product'], row['feature'],
         row['quantity'], row['sum'], row['address'], row['cash_flow_type'])
        )

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()
    
    return None

# функция запроса реализаций из локальной базы данных
def get_sales(date_from=None):
    conn = sqlite3.connect(config.path.database)
    cur = conn.cursor()
    
    if date_from is not None:
        cur.execute(f'SELECT * from sales WHERE date >= ?', (date_from,))
    else:
        cur.execute('SELECT * from sales')
        
    results = cur.fetchall()
    conn.close()
    
    columns_names = ['date', 'sale_id', 'order_date', 'order_id', 'buyer',
                     'contractor', 'site_id', 'product', 'feature',
                     'quantity', 'sum', 'address', 'cash_flow_type']
    
    df = pd.DataFrame(results, columns=columns_names)

    return df
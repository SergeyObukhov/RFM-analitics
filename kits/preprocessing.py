import datetime
import pandas as pd

from config import config
from kits.utilits import send_telegram


# функция предобработки данных
def preprocessing(sales, logger):
    sales['date'] = pd.to_datetime(sales['date'])
    # фильтр по последнему году
    start_date = sales.date.max() - datetime.timedelta(days=364)
    mask_last_year = sales.date >= start_date
    sales = sales[mask_last_year].copy()

    # удалим строки с подарками
    sales  = sales[sales['sum'] >= 10]
    # оставим в данных только те строки, в которых признак 'cash_flow_type' не соответствует значению "Возврат"
    sales = sales.loc[sales['cash_flow_type'] != "Возврат"]
    # удалим за ненадобностью признак 'cash_flow_type'
    sales.drop(['cash_flow_type'], axis=1, inplace=True)

    # перечислим в списке названия наших организаций, которые встречаются в данных после предыдущих обработок
    our_company = ['Суслов Денис Алексеевич ИП', 'Суслов Алексей Александрович ИП', 'Суслова Наталья Джумаевна ИП', 'Кувенева Мария Сергеевна', 'Кувенева Мария Сергеевна ИП']
    # оставим в данных только те строки, которые не соответствуют нашим организациям
    sales = sales.loc[~sales['buyer'].isin(our_company)]

    # удалим строки с пропусками в признаках "ид на сайте", "номер реализации", "сумма", и "количество"
    sales = sales.dropna(axis='index', how='any', subset=['site_id', 'sale_id', 'sum', 'quantity'])

    # сделаем номер реализации уникальным
    # необходимо создать признаки: год, месяц
    sales['year'] = sales['date'].dt.year
    sales['month'] = sales['date'].dt.month

    # изменим тип данных в числовых признаках
    types = {'quantity': 'int16',
            'sum': 'float32',
            'year': 'str',
            'month': 'str'}
    sales = sales.astype(types)

    # сделаем номер реализации уникальным
    sales['sale_id'] = sales['year'] + sales['month'] + '-' + sales['sale_id']
    sales.sort_values(by=['date', 'sale_id'], inplace=True)

    # заполним пропуски ИД заказа
    sales['order_id'] = sales['order_id'].fillna(sales['sale_id'])

    # удалим признак 'address', и 'site_id'
    sales.drop(['site_id', 'address', 'order_date'], axis=1, inplace=True)

    if sales.isnull().sum().sum() > 0:
        logger.warning(f'preprocessing: Gaps in data detected')
        
        send_telegram(
            addr_to=config.tg.addres,
            msg_subj='RFM: Ошибка обработки',
            msg_text=f'В реализациях обнаружены пропуски',
            files=[config.path.logs + config.path.log_file]
        )
    
    return sales, start_date
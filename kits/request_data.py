import requests, json, datetime
import pandas as pd
import numpy as np

from config import config

from kits.utilits import send_telegram
from kits.db_actions import add_sale, get_sales

# определим функцию для приведения новых выгруженных данных к общему виду
def new_sales_formatting(df):
    # заменим пустые строки на NaN
    df = df.replace('', np.nan, regex=True)
    
    # заменим псевдопропуски ('0001-01-01T00:00:00+00:00') на NaN
    df['ДатаЗаказаКлиента'] = df['ДатаЗаказаКлиента'].apply(
        lambda x: np.nan if x == '0001-01-01T00:00:00+00:00' else x
        )

    # подготовим и переформатируем даты
    df['ДатаРегистратора'] = df['ДатаРегистратора'].apply(
        lambda x: x.split('T')[0]
        )
    
    # приведем ид на сайте к строчноому типу, т.к. из-за пропусков добавляется ноль после точки
    df['ИдНаСайте'] = df['ИдНаСайте'].apply(
        lambda x: np.nan if np.isnan(x) else str(int(x))
        )
    
    # переименуем столбцы
    df.columns = ['product', 'feature', 'order_id', 'buyer', 'date', 'sale_id', 'quantity',
                  'sum', 'site_id', 'cash_flow_type', 'contractor', 'address', 'order_date']
    # изменим порядок столбцов
    df = df[['date', 'sale_id', 'order_date', 'order_id', 'buyer', 'contractor', 'site_id',
             'product', 'feature', 'quantity', 'sum',  'address', 'cash_flow_type']]
    
    return df


# функция получения данных по апи ерп
def get_erp_data(start_day, end_day, logger, alg='clasterclients'):
    
    url = config.erp.url
    header = {"Authorization" : config.erp.token}
    
    if not isinstance(start_day, str):
        start_day = str(start_day)
        
    if not isinstance(end_day, str):
        end_day = str(end_day)    
           
    date_start = start_day + "T00:00:00"
    date_end = end_day + "T23:59:59"

    json_request = {
        "datefrom": date_start,
        "datebefore": date_end,
        "algoritm": alg
    }

    response = requests.post(url, headers=header, json=json_request)
    
    if response.status_code == 200:
        if alg == 'clasterclients':
            return new_sales_formatting(            # форматируем даты, названия, и порядок колонок
                pd.json_normalize(                  # преобразуем json в Pandas Data Frame
                    json.loads(                     # преобразуем данные в json
                        response.json()['data']     # достаём данные из ответа ЕРП
                        )
                    )
                )
        elif alg == 'partnersdata':
            return pd.json_normalize(               # преобразуем json в Pandas Data Frame
                json.loads(                         # преобразуем данные в json
                    response.json()['data']         # достаём данные из ответа ЕРП
                    )
                )
        else: return None
    else:
        logger.error(f'get_erp_data: {alg}: response.status_code: {response.status_code}')
        
        send_telegram(
            addr_to=config.tg.addres,
            msg_subj='RFM: Ошибка запроса',
            msg_text=f'get_erp_data: {alg}: response.status_code: {response.status_code}',
            files=[config.path.logs + config.path.log_file]
        )
        
    return None


# функция актуализации локальной базы данных
def refresh_sales_base(logger):
    # СУТЬ: реализации могут появиться в ерп постфактум,
    # поэтому будем каждый день проверять не появились ли реализации за последний месяц

    yesterday = str(datetime.datetime.today().date() - datetime.timedelta(days=1))
    # возьмем данные за последний месяц из реализаций в нашей базе
    month_ago = str(datetime.datetime.today().date() - datetime.timedelta(days=30))
    # найдем последнюю дату
    date_max_in_sales = get_sales(month_ago).date.max()
    # если последние данные за вчерашний день, прерываем обновление данных
    if date_max_in_sales == yesterday:
        return None

    # дата начала запроса будет начинаться за месяц от уже имеющихся данных в нашей базе
    start_date = str(datetime.datetime.strptime(date_max_in_sales, '%Y-%m-%d').date() - datetime.timedelta(days=30))

    # загрузим продажи из нашей базы
    sales_in_base = get_sales(start_date)
    sales_in_base.drop_duplicates(inplace=True)

    # загрузим продажи из ерп
    sales_from_erp = get_erp_data(start_date,
                                  yesterday,
                                  logger,
                                  alg='clasterclients')
    sales_from_erp.drop_duplicates(inplace=True)

    # нужно определить строки из ерп, которые ещё не были загружены в нашу базу
    concat_df = pd.concat([sales_in_base, sales_from_erp])
    # subtrahend - вычитаемое
    subtrahend_df = concat_df[concat_df.duplicated()]
    # уберем строки, которые уже были загружены, чтобы не загружать их повторно
    concat_df = pd.concat([sales_from_erp, subtrahend_df])
    result_df = concat_df.drop_duplicates(keep=False)

    # загрузим новые данные в нашу базу
    for _, row in result_df.iterrows():
        add_sale(row)
        
    return None


# функция для обновления, и получения данных по реализациям и клиентам
def loading_data(logger):
    # загрузим новые данные в нашу базу
    refresh_sales_base(logger)    
        
    # запрос в ерп данных по покупателям
    start_buyers_date = datetime.datetime.strptime('2021-12-31', '%Y-%m-%d').date()
    yesterday = datetime.datetime.today().date() - datetime.timedelta(days=1)
    buyers_data = get_erp_data(start_buyers_date,
                               yesterday,
                               logger,
                               alg='partnersdata')
    buyers_data = buyers_data.replace('', np.nan, regex=True)
    buyers_data.columns = ['buyer', 'email', 'category']
    buyers_data = buyers_data[['buyer', 'email']] #, 'category', 'email']]
    buyers_data.dropna(subset=['buyer'], inplace=True)
    # buyers_data['category'] = buyers_data['category'].fillna('не заполнено')
  
    # загрузим данные по продажам
    start_day = str(datetime.datetime.today().date() - datetime.timedelta(days=370))
    sales = get_sales(date_from=start_day)
        
    return sales, buyers_data
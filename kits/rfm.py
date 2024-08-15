import statistics as stat
import datetime

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from kits.sales_analitic import show_values, date_on_fig


# функция rfm обработки
def rfm_processing(sales):
    # RFM классификатор
    def get_state(features):
        
        if (features['Frequency'] >= 12) & (features['Monetary'] >= 600000) & (features['Recency'] < 90):
            return '1.ЧЕМПИОНЫ'
        
        if features['Frequency'] >= 9:
            
            if features['Recency'] >= 180:
                return '4.ЗОНА ПОТЕРИ'
            elif features['Recency'] >= 90:
                return '3.ЗОНА РИСКА'
            else:
                return '2.ЛОЯЛЬНЫЕ'
        
        # F-3
        elif (features['Frequency'] >= 6) & (features['Monetary'] >= 300000) & (features['Recency'] < 90):
            return '5.РАЗВИВАЮЩИЕСЯ'
        
        elif (features['Frequency'] >= 3) & (features['Monetary'] >= 100000) & (features['Recency'] < 90):
            return '6.ПЕРСПЕКТИВНЫЕ'
        
        # F-2
        elif features['Frequency'] >= 3:
            
            if features['Recency'] > 135:
                return '9.СПЯЩИЕ'
            elif features['Recency'] > 45:
                return '8.ДРЕЙФУЮЩИЕ'
            else:
                return '6.ПЕРСПЕКТИВНЫЕ'
        
        #F-1
        else:
            
            if features['Recency'] > 135:
                return '9.СПЯЩИЕ'
            elif features['Recency'] > 45:
                return '8.ДРЕЙФУЮЩИЕ'
            else:
                return '7.НОВИЧКИ'
            
        return np.nan

    # оптовый классификатор
    def get_wholesale(mean_sum):
        
        if mean_sum >= 500000:
            return '1.Кит'
        elif mean_sum >= 220000:
            return '2.Крупный оптовик'
        elif mean_sum >= 100000:
            return '3.Оптовик'
        elif mean_sum >= 30000:
            return '4.Мелкий оптовик'
        else:
            return '5.Розничный'

    # определим функцию, которая считает временные интервалы каждого пользователя
    def get_time_slots(dates):
        
        if len(dates) < 2:
            return [0]
                
        time_slots = []
        first_date = ''
        
        for date in dates:
                date = str(date)
                if first_date == '':
                    first_date = date
                    continue
                delta = (datetime.datetime.strptime(first_date, "%Y-%m-%d") -
                        datetime.datetime.strptime(date, "%Y-%m-%d")
                        )
                time_slots.append(delta.days)
                first_date = date
                
        return time_slots

    #
    def get_mean_interval(t_slots):
        def deep_index(t_s, deep=120):
            sum = 0
            # ищем индекс интервала, где сумма будет больше нужной глубины
            for i in range(len(t_s)):
                sum += t_s[i]
                if sum > deep:
                    # этот индекс и будет пороговым в срезе
                    return i
        
        if len(t_slots) == 0: # если покупка одна
            return 0
        elif len(t_slots) == 1:
            return t_slots[0]
        
        # если последний интервал больше 4 месяцев, т. е. клиент засыпал
        if t_slots[0] > 120:
            # для новичков - нет статистики (нет сл. 3-х инт.-лов)
            if len(t_slots) < 5:
                return t_slots[0]
            # берём три следующих интервала
            else:
                return round(stat.mean(t_slots[1:4]))
        
        # если всреднем покупает чаще чем раз в месяц
        elif stat.mean(t_slots[0:3]) < 30:
            # берём статистику за последние 4 месяца
            return round(stat.mean(t_slots[0:deep_index(t_slots, deep=120)]))
        # иначе берём статистику за последние 6 месяцев
        else: 
            return round(stat.mean(t_slots[0:deep_index(t_slots, deep=180)]))

    #
    def get_orders_interval(df):
        # сгруппируем продажи по заказам фиксируя даты
        orders_dates = (
            df
            .groupby(['buyer', 'order_id'])['date'].min()
            .dt.to_period("D")
            .reset_index()
            .sort_values(by='date', ascending=False)
            .groupby('buyer')['date'].unique()
            .reset_index()
            )

        orders_dates['time_slots'] = orders_dates['date'].apply(get_time_slots)
        orders_dates['mean_interval_orders'] = orders_dates['time_slots'].apply(get_mean_interval)
        orders_dates.drop(['date' ,'time_slots'], axis=1, inplace=True)
        
        return orders_dates

    # посчитаем количество заказов каждого клиента
    rfm_table = sales.groupby('buyer').order_id.nunique().reset_index()

    # определим день точки отсчета
    t_0 = sales.date.max() + datetime.timedelta(days = 1)
    # посчитаем давность последней покупки: из дня точки отсчета вычтем дату последней покупки
    recency = sales.groupby('buyer').date.max().apply(lambda x: t_0 - x)
    # выразим давность в днях
    recency = recency.dt.days.reset_index()
    # добавим данные в таблицу
    rfm_table = rfm_table.merge(recency)

    # рассчитаем общие суммы, которые потратил каждый клиент
    monetary_value = sales.groupby('buyer')['sum'].sum().reset_index()
    # добавим данные в таблицу
    rfm_table = rfm_table.merge(monetary_value)

    # добавим интервалы в rfm-таблицу
    rfm_table = rfm_table.merge(get_orders_interval(sales), on='buyer', how='left')

    # добавим признак '2month' для будущего анализа оптовиков
    sales.month = sales.month.astype('int8')
    sales['2month'] = sales['month'].apply(lambda x: x if int(x)%2 == 1 else x-1)
    
    # посчитаем среднюю 2 месячную сумму заказа каждого клиента
    mean_sums = (
        sales
        # посчитаем сумму заказов за каждые пару месяцев
        .groupby(['buyer', '2month'])['sum'].sum()
        .reset_index()
        # посчитаем среднее для каждого клиента
        .groupby('buyer')['sum'].mean()
        .reset_index()
        )
    # добавим данные в таблицу
    rfm_table = rfm_table.merge(mean_sums, on='buyer')

    # признак покупателя переведем в индекс
    rfm_table.set_index('buyer', inplace=True)
    # переименуем столбцы
    rfm_table.columns = ['Frequency', 'Recency', 'Monetary', 'Interval', 'mSum']
    rfm_table = rfm_table[['Recency', 'Frequency', 'Monetary', 'Interval', 'mSum']]
    rfm_table = rfm_table.round(2).astype('int64')

    rfm_table['state'] = rfm_table.apply(get_state, axis=1)
    rfm_table['wholesale'] = rfm_table['mSum'].apply(get_wholesale)

    # удалим признак 'mSum'
    rfm_table.drop(['mSum'], axis=1, inplace=True)

    rfm_table.reset_index(inplace=True)
        
    return rfm_table


# функция экспорта rfm-аналитики в виде ексель файла
def rfm_export(rfm_df, buyers_df, upload_path):
    rfm_df = rfm_df.join(
        buyers_df.set_index('buyer'),
        on='buyer',
        how='left'
    )

    rfm_df = rfm_df.sort_values(by=['wholesale', 'state'], ascending=False)
    true_columns = rfm_df.columns
    # переименуем столбцы для выгрузки
    columns_list = ['Покупатель', 'Давность, дней', 'Число заказов', 'Потратил, руб',
                    'Частота заказов, дней', 'RFM сегмент', 'Оптовый сегмент', 'Почта']
    rfm_df.columns = columns_list

    # выгрузим rfm-таблицу
    with pd.ExcelWriter(upload_path + 'RFM.xlsx', engine='xlsxwriter') as wb:
        rfm_df.to_excel(wb, sheet_name='Sheet1', index=False)
        sheet = wb.sheets['Sheet1']

        sheet.set_column('A:A', 35)
        sheet.set_column('B:E', 10)
        sheet.set_column('F:G', 15)
        sheet.set_column('H:H', 25)
        
        sheet.set_row(0, 45)
        cell_format = wb.book.add_format({'bold': True,         # жирный шрифт
                                          'text_wrap': True,    # перенос строки
                                          'valign': 'top',      # вертикальное выравнивание
                                          'align': 'center',    # горизонтальное выравнивание
                                          'border': 2})         # граница
        format = wb.book.add_format({'font_size': 16, 'bold': True})
        sheet.write_row(0, 0, columns_list, cell_format)        # заполним первую строку с названиями колонок
        sheet.freeze_panes(1, 0)                                # закрепить строку
        sheet.autofilter(0, 0, 0, len(columns_list)-1)          # автофильтр
        sheet.write(0, len(columns_list), 'все данные расчитаны за период: 365 дней', format)

    # вернём изначальные названия колонок
    rfm_df.columns = true_columns
    
    return rfm_df

# функция визуализации аналитики
def rfm_analitic(rfm_df, upload_path, start_date):

    features = ['wholesale', 'state']
    feaure_titles = ['уровню опта', 'RFM-cегментам']

    for i, feature in enumerate(features):
        if rfm_df[feature].nunique() == 9:
            colors_list = None#['silver', 'darkgoldenrod', 'lightskyblue', 'darkviolet', 'chartreuse', 'green', 'slateblue', 'coral', 'red']
        elif rfm_df[feature].nunique() == 5:
            colors_list = None#['green', 'chartreuse', 'slateblue', 'lightskyblue', 'darkviolet']
        #Строим количественную столбчатую для долевого соотношения каждой из категорий в данных
        count_data = ((rfm_df[feature].value_counts(normalize=True)*100)
                    .sort_values(ascending=False)
                    .rename('Процентов')
                    .reset_index())
        
        fig = plt.figure(figsize=(10, 5));
        barplot = sns.barplot(data=count_data, x='index', y='Процентов', palette=colors_list)
        barplot.set_title('Соотношение по ' + feaure_titles[i] + ' ' + date_on_fig(start_date));
        barplot.set_xlabel('Соотношение по ' + feaure_titles[i]);
        barplot.xaxis.set_tick_params(rotation=14)
        show_values(barplot, float_deep=1)
        
        fig.savefig(upload_path + 'партнеры_по_' + feaure_titles[i] + '.png')
        
    pivot = rfm_df.pivot_table(
        values='buyer',
        index='state',
        columns='wholesale',
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name = 'Всего'
    )

    fig = plt.figure(figsize=(16, 6))
    heatmap = sns.heatmap(data=pivot, annot=True, fmt ='.0f', cmap='Blues', vmax=pivot.loc['9.СПЯЩИЕ', '5.Розничный']);

    heatmap.set_title('Распределение клиентов по уровню опта и RFM-сегментам', fontsize=16);
    heatmap.set_xlabel('Уровень опта');
    heatmap.set_ylabel('RFM-сегменты');
    # heatmap.xaxis.set_tick_params(rotation=8);

    # сохраним таблицу и данные
    fig.savefig(upload_path + 'распределение_кластеров.png')
    
    return None
import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("whitegrid")

# функция для отображения значений на гистограмме sns
def show_values(axs, orient="v", space=.01, float_deep=0, divider=1):
    # get float format like '{:.3f}'
    value_format = '{:.' + str(float_deep) + 'f}'
    def _single(ax):
        if orient == "v":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 2
                _y = p.get_y() + p.get_height() + (p.get_height() * 0.01)                
                value = value_format.format(p.get_height()/divider)
                ax.text(_x, _y, value, ha="center") 
        elif orient == "h":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(space)
                _y = p.get_y() + p.get_height() - (p.get_height() * 0.5)
                value = value_format.format(p.get_width())
                ax.text(_x, _y, value, ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _single(ax)
    else :
        _single(axs)

# функция для форматирования дат на графиках     
def date_on_fig(start_date):  
    def format_date(date):
        return '.'.join(str(date).split('-'))
    
    yesterday = str(datetime.datetime.today().date() - datetime.timedelta(days=1))
    
    return f'({format_date(str(start_date.date()))} - {format_date(str(yesterday))})'


# визуализация заказов
def plot_orders(sales, upload_path, start_date):
    # сгруппируем данные по заказам, и сосчитаем суммы и количества
    sales_sum = sales.groupby(by='order_id')['sum', 'quantity'].sum().reset_index()

    # построим гистограммы
    fig = plt.figure(figsize=(10,5))
    his1 = sns.histplot(
        data=sales_sum[sales_sum['sum'] < 100000]['sum'] /1000,
        bins=25,
        kde=True
    );
    his1.set_title('Суммы заказов ' + date_on_fig(start_date));
    his1.set_xlabel('Сумма заказов, тыс. руб.');
    his1.set_ylabel('Количество заказов');
    show_values(his1, float_deep=1, divider=1000)
    fig.savefig(upload_path + 'суммы_заказов.png')

    print()

    fig = plt.figure(figsize=(10,5))
    his2 = sns.histplot(
        data=sales_sum[sales_sum['quantity'] < 170],
        x='quantity',
        bins=30,
        kde=True
    );
    his2.set_title('Количество товаров в заказах ' + date_on_fig(start_date));
    his2.set_xlabel('Количество товаров, шт.');
    his2.set_ylabel('Количество заказов');
    show_values(his2, float_deep=1, divider=1000)
    fig.savefig(upload_path + 'товары_в_заказах.png')
        
    return None

# визуализация заказов по месяцам
def plot_orders_months(sales, upload_path, start_date):
    # сгруппируем данные просумировав выручку от заказов по каждому месяцу
    revenue_month = sales.groupby(by='month')['sum'].sum() / 1000000

    # построим визуализацию, отражающую распределение суммы заказов по месяцам
    fig = plt.figure(figsize=(10, 4))
    barplot = sns.barplot(
        x=revenue_month.index,
        y=revenue_month.values
    )
    barplot.set_title('Распределение суммы заказов по месяцам ' + date_on_fig(start_date));
    plt.ticklabel_format(style='plain', axis='y')
    barplot.set_xlabel('Месяц')
    barplot.set_ylabel('Сумма от заказов, млн. руб.');
    show_values(barplot, float_deep=1)
    fig.savefig(upload_path + 'суммы_по_месяцам.png')

    print()

    # посчитаем количество заказов в каждом месяце
    orders_months = sales.groupby(by='month')['order_id'].nunique() / 1000

    # построим визуализацию, отражающую распределение оличества заказов по месяцам
    fig = plt.figure(figsize=(10, 4))
    barplot = sns.barplot(
        x=orders_months.index,
        y=orders_months.values
    )
    barplot.set_title('Распределение количества заказов по месяцам ' + date_on_fig(start_date));
    plt.ticklabel_format(style='plain', axis='y')
    barplot.set_xlabel('Месяц')
    barplot.set_ylabel('Количество заказов, тыс.');
    show_values(barplot, float_deep=1)
    fig.savefig(upload_path + 'заказы_по_месяцам.png')

    print()

    # посчитаем количество покупателей в каждом месяце
    count_buyers_month = sales.groupby(by='month')['buyer'].nunique() / 1000

    # построим визуализацию, отражающую распределение количества покупателей по месяцам
    fig = plt.figure(figsize=(10, 4))
    barplot = sns.barplot(
        x=count_buyers_month.index,
        y=count_buyers_month.values
    )
    barplot.set_title('Распределение количества покупателей по месяцам ' + date_on_fig(start_date));
    plt.ticklabel_format(style='plain', axis='y')
    barplot.set_xlabel('Месяц')
    barplot.set_ylabel('Количество покупателей, тыс.');
    show_values(barplot, float_deep=1)
    fig.savefig(upload_path + 'покупатели_по_месяцам.png')
        
    return None


# визуализация ТОП покупателей
def plot_top_buyers(sales, upload_path, start_date):
    # посчитаем сколько потратил каждый покупатель, и отсоритруем по убыванию
    customer_top = sales.groupby(["buyer"])['sum'].sum().sort_values(ascending = False)

    # посчитаем процент топ 50-ти от общей суммы продаж за 3 года
    percent_sales = np.round((customer_top[:51].sum() / customer_top.sum()) * 100, 2)

    fig = plt.figure(figsize=(16, 8))
    barplot = sns.barplot(
        x=customer_top[:51].index,
        y=customer_top[:51].values/1000000
    )
    barplot.set_title('Топ 50 покупателей: {:3.2f}% от общей суммы продаж '.format(percent_sales) + date_on_fig(start_date));
    barplot.set_xlabel('Покупатель')
    barplot.set_ylabel('Сумма от заказов, млн. руб.');
    plt.xticks(rotation=90)
    show_values(barplot)
    fig.savefig(upload_path + 'топ50_покупателей_суммы.png')
        
        
    return None

# визуализация ТОП продаваемых товаров
def plot_top_products(sales, upload_path, start_date):
    # сгруппируем данные по товарам, просуммировав выручку
    goods_sum_top = sales.groupby(["product"])['sum'].sum().sort_values(ascending = False)
    # сгруппируем данные по товарам, просуммировав количество заказов, в которых фигурировал этот товар
    goods_orders_top = sales[["product", "order_id"]].groupby(["product"]).order_id.nunique().sort_values(ascending = False)

    # запишем в список топ 10 продуктов по сумме продаж
    top10 = list(goods_sum_top[:10].index)
    # посчитаем проценты по суммам продаж и количеству реализаций
    percent_sales =  np.round((goods_sum_top[top10].sum()/goods_sum_top.sum()) * 100, 2)
    percent_events = np.round((goods_orders_top[top10].sum()/goods_orders_top.sum()) * 100, 2)

    # построим диаграмму
    fig = plt.figure(figsize=(10, 8));
    barplot = sns.barplot(
        x=goods_sum_top[top10].index,
        y=goods_sum_top[top10].values/1000000
    );
    barplot.set_title('Топ 10 продуктов по сумме продаж: {:3.2f}% от общей суммы продаж и {:3.2f}% от заказов '.format(percent_sales, percent_events) + date_on_fig(start_date), fontsize=10);
    barplot.set_xlabel('Товар');
    barplot.set_ylabel('Сумма от продаж, млн. руб.');
    plt.xticks(rotation=90)
    show_values(barplot, float_deep=1)
    fig.savefig(upload_path + 'топ10_продуктов_суммы.png')

    # запишем в список топ 10 продуктов по количеству реализаций
    top10ev = list(goods_orders_top[:10].index)
    # посчитаем проценты по суммам продаж и количеству реализаций
    percent_sales =  np.round((goods_sum_top[top10ev].sum()/goods_sum_top.sum()) * 100, 2)
    percent_events = np.round((goods_orders_top[top10ev].sum()/goods_orders_top.sum()) * 100, 2)

    # построим диаграмму
    fig = plt.figure(figsize=(10, 8));
    barplot = sns.barplot(
        x=goods_orders_top[top10ev].index,
        y=goods_orders_top[top10ev].values/1000
    );
    barplot.set_title('Топ 10 продуктов по заказам: {:3.2f}% от общей суммы продаж и {:3.2f}% от заказов '.format(percent_sales, percent_events) + date_on_fig(start_date), fontsize=10);
    barplot.set_xlabel('Товар');
    barplot.set_ylabel('Количество заказов, тыс. шт.');
    plt.xticks(rotation=90)
    show_values(barplot, float_deep=1)
    fig.savefig(upload_path + 'топ10_продуктов_заказы.png')        
        
    return None
from multiprocessing import Process
import os, shutil, psutil
import schedule, datetime, time

from kits.utilits import get_logger, send_telegram, error_trapping
from kits.request_data import loading_data
from kits.preprocessing import preprocessing
from kits.rfm import rfm_processing, rfm_analitic, rfm_export
from kits.sales_analitic import plot_orders, plot_orders_months

from config import config

# ежедневный регламентный скрипт
def daily_script():
    global logger
    
    logger.info(f'daily_script: START script')
    logger.info(f'daily_script: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    
    # загрузка данных
    data, buyers = loading_data(logger)
    
    logger.info(f'daily_script: LOADED data')
    logger.info(f'daily_script: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    
    # предобработка
    data, start_date = preprocessing(data, logger)

    logger.info(f'daily_script: PREPROCESSED data')
    logger.info(f'daily_script: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')

    # RFM обработка
    rfm_data = rfm_processing(data)
    
    logger.info(f'daily_script: RFM processed')
    logger.info(f'daily_script: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    
    # графики и отчет
    # сгенерируем путь для выгрузки
    yesterday = str(datetime.datetime.today().date() - datetime.timedelta(days=1))
    upload_path = config.path.project + 'upload/' + yesterday + '/'
    logger.info(f'daily_script: upload_path generated: {upload_path}')
    # создадим папку для выгрузки
    if not os.path.isdir(upload_path): # если нет папки - создаем
        os.mkdir(upload_path)
    
    rfm_data = rfm_export(rfm_data, buyers, upload_path)
    rfm_analitic(rfm_data, upload_path, start_date)
    
    plot_orders(data, upload_path, start_date)
    plot_orders_months(data, upload_path, start_date)
    # plot_top_buyers(data, upload_path, start_date)
    # plot_top_products(data, upload_path, start_date)
    
    
    shutil.copytree(upload_path, config.path.analyts + yesterday)
    shutil.copytree(upload_path, config.path.marketers + yesterday)
    
    logger.info(f'daily_script: END script')
    logger.info(f'daily_script: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    
    send_telegram(
        addr_to=config.tg.addres,
        msg_subj='RFM:',
        msg_text='Успешное выполнение!',
        files=[config.path.logs + config.path.log_file]
    )
    
    return None

# декоратор для передачи объекта logger в функцию
def error_cath():
    global logger
    
    error_trapping(daily_script, logger)
    return None
    

# запуск ежедневного скрипта отдельным процессом
def run_process(func):
    global logger
    
    proc = Process(target=func)
    logger.info(f'run_process: Proc is_alive status: {proc.is_alive()}')
    logger.info(f'run_process: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    proc.start()
    logger.info(f'run_process: Proc is_alive status: {proc.is_alive()}')
    proc.join()
    logger.info(f'run_process: Proc is_alive status: {proc.is_alive()}')
    logger.info(f'run_process: Used memory: {psutil.virtual_memory().used / 1024 / 1024:.3f} MB')
    
    return None

logger = get_logger(path_log=config.path.logs, file=config.path.log_file)

schedule.every().day.at("02:00").do(run_process, error_cath)

while True:
    schedule.run_pending()
    time.sleep(60)
import telebot, traceback, os, sys, datetime, logging
from config import config

# функция инициализации объекта logger
def get_logger(path_log, file):
    """[Создает лог-файл для логирования в него]
    Аргументы:
        path {string} -- путь к директории
        file {string} -- имя файла
    Возвращает:
        [obj] -- [логер]
    """
    # проверяем, существует ли файл
    log_file = os.path.join(path_log, file)
 
    #если  файла нет, создаем его
    if not os.path.isfile(log_file):
        open(log_file, "w+").close()
  
    # поменяем формат логирования
    file_logging_format = "%(levelname)s: %(asctime)s: %(message)s"
  
    # конфигурируем лог-файл
    logging.basicConfig(level=logging.INFO,
                        format = file_logging_format)
    logger = logging.getLogger()
  
    # создадим хэнлдер для записи лога в файл
    handler = logging.FileHandler(log_file)
  
    # установим уровень логирования
    handler.setLevel(logging.INFO)
  
    # создадим формат логирования, используя file_logging_format
    formatter = logging.Formatter(file_logging_format)
    handler.setFormatter(formatter)
  
    # добавим хэндлер лог-файлу
    logger.addHandler(handler)
    return logger


# функция отправки уведомлений в телеграмм
def send_telegram(addr_to, msg_subj, msg_text, files=[]):
    
    TOKEN = config.tg.token

    bot = telebot.TeleBot(TOKEN)
    
    bot.send_message(addr_to, text=msg_subj+'\n'+msg_text)
    for file in files:
        bot.send_document(addr_to, open(file, 'rb'))
    
    return None


# функция перехвата ошибки, и отправки уведомления админу в телеграм
def error_trapping(func, logger):
    
    try:
        func()
    except BaseException as ex:
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        logger.warning('error_trapping: WARNING!!!')
        logger.critical('The process crashed due to an error:')
        logger.error("Exception type : " + str(ex_type.__name__))
        logger.error("Exception message : " + str(ex_value))
        logger.error("Stack trace :")
        for line in stack_trace:
            logger.error(str(line))
    
        time_now = str(datetime.datetime.now().time()).split(':')
        message_text = ['\t Ошибка случилась в ', str(time_now[0]), 'часов', str(time_now[1]), 'минут \n',
            'Exception type :', str(ex_type.__name__), '\n',
            'Exception message :', str(ex_value),  '\n',
            'Stack trace : \n']
        for line in stack_trace:
            message_text.append(str(line) + ' \n')

        send_telegram(
            addr_to=config.tg.addres,
            msg_subj='RFM: Ошибка выполнения в программе!',
            msg_text=" ".join(message_text),
            files=[config.path.logs + config.path.log_file]
        )

        logger.info('error_trapping: Error message sent to: Sergey telegram')
    return None
from dataclasses import dataclass
from environs import Env


@dataclass
class Path:
    project: str        # Путь к проекту
    data: str           # Путь к данным
    logs: str           # Путь к логам
    log_file: str       # Имя лог файла
    analyts: str        # Путь к сетевой папке Аналитики
    marketers: str      # Путь к сетевой папке Маркетологи
    database: str       # Путь к файлу базы данных

@dataclass
class Erp:
    url: str            # Ссылка для подключению к апи ерп
    token: str          # Токен апи ерп

@dataclass
class Tg:
    addres: str         # Адрес для отправки сообщений
    token: str          # Токен для передачи сообщений по телеграм

@dataclass
class Config:
    path: Path
    erp: Erp
    tg: Tg

# Создаем экземпляр класса Env
env: Env = Env()

# Добавляем в переменные окружения данные, прочитанные из файла .env 
env.read_env()

# Создаем экземпляр класса Config и наполняем его данными из переменных окружения
config = Config(
    path=Path(
        project=env('PROJECT_PATH'),
        data=env('DATA_PATH'),
        logs=env('LOGS_PATH'),
        log_file=env('LOG_FILE'),
        analyts=env('ANALYTS_PATH'),
        marketers=env('MARKETERS_PATH'),
        database=env('DATABASE')
    ),
    erp=Erp(
        url=env('ERP_URL'),
        token=env('ERP_TOKEN')        
    ),
    tg=Tg(
        addres=env('TG_ADDRESS'),
        token=env('TG_TOKEN')
    )
)


# Выводим значения полей экземпляра класса Config на печать, 
# чтобы убедиться, что все данные, получаемые из переменных окружения, доступны
print('PROJECT_PATH:\t', config.path.project)
print('DATA_PATH:\t', config.path.data)
print('LOGS_PATH:\t', config.path.logs)
print('LOG_FILE:\t', config.path.log_file)
print('ANALYTS_PATH:\t', config.path.analyts)
print('MARKETERS_PATH:\t', config.path.marketers)
print()
print('ERP_URL:\t', config.erp.url)
print('ERP_TOKEN:\t', config.erp.token)
print()
print('TG_ADDRESS:\t', config.tg.addres)
print('TG_TOKEN:\t', config.tg.token)
print()
print('DATABASE:\t', config.path.database)
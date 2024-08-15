# Сервис RFM-аналитики клиентов

![Текст с описанием картинки](/data/rfm_segments.jpg)


## Оглавление  
[1. Описание проекта](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#описание-проекта)  
[2. Какой кейс решаем?](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#какой-кейс-решаем)  
[3. Краткая информация о данных](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#краткая-информация-о-данных)  
[4. Этапы работы над проектом](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#этапы-работы-над-проектом)  
[5. Результаты](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#результаты)  
[6. Выводы](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#выводы)  
  
### Описание проекта  
Интернет магазину необходимо сегментировать наработанную клиентскую базу, чтобы эффективнее таргетировать маркетинговые компании.

В этом проекте мы реализуем модель классификации клиентов на основе их покупательской способности, частоты заказов и срока давности последней покупки. 
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)  
  
  
### Какой кейс решаем?  
Необходим сервис, который ежедневно отслеживает продажи, сегментирует клиентов, и предоставляет отчеты.  
  
**Внедрение результатов исследования:**  
Проект основан на ранее проведенном исследовании: [Проект](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_7)
  
**Функционал приложения**  
- Приложение ежедневно получает данные по апи из программы 1С:ЕРП
- Хранит полученные данные в локальной базе данных для быстрого доступа
- Подготавливает данные для дальнейшей классификации
- Обрабатывает, и классифицирует клиентов
- Визуализирует ключевые показатели, и распределения
- Формирует отчет, и кладет в необходимую сетевую папку
- В приложении организован механизм перехвата ошибок, без остановки сервиса
- Есть возможность отправки уведомлений в телеграм, в том числе сообщений об ошибках админу, с отправкой логов

  
**Основные билиотеки:**  
- pandas
- requests
- sqlite3
- schedule
- multiprocessing
- telebot
- statistics
- matplotlib
- seaborn
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)  

### Краткая информация о данных  
....  
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)  
  
  
### Этапы работы над проектом  
1. [game.py](https://github.com/SergeyObukhov/sf_data_science/blob/main/projekt_0/game.py) - Написали программу, в которой пользователю при помощи диалога предлагается отгадать число, загаданное компьютером.
2. [game_v2.py](https://github.com/SergeyObukhov/sf_data_science/blob/main/projekt_0/game_v2.py) - Добавили две функции. Одна случайным образом угадывает число. А вторая вычисляет среднее колличество попыток, за которое первая функция угадывает загаданное число.  
3. [game_v3.py](https://github.com/SergeyObukhov/sf_data_science/blob/main/projekt_0/game_v3.py) - Написал алгоритм, который учитывает, больше ли случайное число или меньше нужного нам числа. Функция сокращает диапазон значений, уменьшая его вдвое на каждой итерации цикла. 
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)  
  
  
### Результаты  
- Мой алгоритм угадывает число в среднем за 5 попыток.
- Я попрактиковался в написании хорошего кода на Python.  
- Я отработал приемы использования IDE.
- Оформил свой первый проект на GitHub.
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)  
  
  
### Выводы  
Я справился с поставленной задачей: написать функцию, которая будет угадывать число меньше чем за 20 попыток.  
Я благодарен автору модуля и всему проекту SF за переданные мне навыки.
  
:arrow_up: [к оглавлению](https://github.com/SergeyObukhov/sf_data_science/tree/main/projekt_0#оглавление)
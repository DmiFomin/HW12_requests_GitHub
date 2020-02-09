import os
import json
import pprint
import base64
import re
import requests
import sqlite3
import datetime


def get_cursor():
    '''
    Получаем подключение к MSLite и курсор
    :return: возвращаем подключение и курсор
    '''
    conn = sqlite3.connect('C:\\Users\\fomin\\DataBases_SQLite\\db_CheckingGitHub.db', check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor


def get_program_settings():
    """
    Получаем настройки программы
    :return: Возвращаем словарь с настройками
    """
    # unsafe_codes = [{'language': 'python', 'string_code': 'eval', 'description': 'В коде есть функция eval.',  'add_description': 'В функцию eval, возможно, передано значение из внешнего источника.', 'status': 'Потенциально опасен'},
    #                 {'language': 'python', 'string_code': 'sqlite3', 'description': 'В коде есть sql инъекция.', 'add_description': '', 'status': 'Содержит уязвимость'},
    #                 {'language': 'python', 'string_code': 'pickle', 'description': 'В коде используется модуль pickle.', 'add_description': 'В функцию pickle.load(), возможно, передаются данные из стороннего источника.', 'status': 'Потенциально опасен'},
    #                 {'language': 'python', 'string_code': 'EMAIL_HOST_USER', 'description': 'Явно указан email.', 'add_description': '', 'status': 'Содержит уязвимость'},
    #                 {'language': 'python', 'string_code': 'EMAIL_HOST_PASSWORD', 'description': 'Явно указаны пароли от email.', 'add_description': '', 'status': 'Содержит уязвимость'}
    #                ]
    #
    # program_settings = {'path_to_token': os.path.join(os.getcwd(), 'GitHub_Token'),
    #                     'unsafe_codes': unsafe_codes,
    #                     'author': 'Фомин Дмитрий',
    #                     'phone': '8-123-123-12-12',
    #                     'email': 'email@email.com'}

    unsafe_codes = []
    program_settings = {}

    # Получаем список уязвимостей
    conn, cursor = get_cursor()
    cursor.execute('SELECT us.language, us.string_code, us.description, us.add_description, s.description FROM Unsafe_codes us, Statuses s WHERE us.status = s.id')
    result_unsafe_codes= cursor.fetchall()

    for item in result_unsafe_codes:
        unsafe_codes.append({'language': item[0],
                             'string_code': item[1],
                             'description': item[2],
                             'add_description': item[3] if item[3] != None else '',
                             'status': item[4]})


    # Получаем информацию о программе
    cursor.execute('SELECT * FROM Settings')
    result_settings = cursor.fetchall()[0]

    program_settings = {'path_to_token': os.path.join(os.getcwd(), result_settings[1]),
                        'unsafe_codes': unsafe_codes,
                        'author': result_settings[2],
                        'phone': result_settings[3],
                        'email': result_settings[4]}

    conn.close()
    return program_settings


def load_token(path):
    '''
    Загружаем токен GitHub
    :param path: - путь до файла
    :return: - токен
    '''
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                result = f.readline()
                return result
        except Exception as e:
            print(e)
            print('Файл с токеном GitHub не обнаружен!')


def external_source(content):
    '''
    Ищем в модуле вхождение "токсичных" строк
    :param content: контент модуля
    :return: булево
    '''
    return '.read()' in content or 'input' in content or 'open('


# Решил для каждой проверки сделать свою функцию.
def check_eval(decoded_content, element_unsafe_code):

    result_list = []
    if 'eval(' in decoded_content:
        if external_source(decoded_content):
            result_list.append({'description': element_unsafe_code['add_description'], 'status': 'Содержит уязвимость.'})
        else:
            result_list.append({'description': element_unsafe_code['description'], 'status': element_unsafe_code['status']})

    return result_list


def check_SQL(decoded_content):

    result_SELECT = re.search(r"f'*select.+from*", decoded_content.lower())
    result_SELECT_format = re.search(r"select.+from.+\.format", decoded_content.lower())
    result_INSERT = re.search(r"f'*insert into*", decoded_content.lower())
    result_INSERT_format = re.search(r"insert into.+\.format", decoded_content.lower())
    result_UPDATE = re.search(r"f'*update.+set*", decoded_content.lower())
    result_UPDATE_format = re.search(r"update.+set.+\.format", decoded_content.lower())
    result_DELETE = re.search(r"f'*delete.+from*", decoded_content.lower())
    result_DELETE_format = re.search(r"delete.+from.+\.format", decoded_content.lower())

    result_list = []
    if result_SELECT != None or result_SELECT_format != None:
        if external_source(decoded_content):
            result_list.append({'description': 'В коде есть SQL запрос SELECT с получением данных из внешнего источника и, возможно, выполняется напрямую в БД.', 'status': 'Содержит уязвимость.'})

    if result_INSERT != None or result_INSERT_format != None:
        if external_source(decoded_content):
            result_list.append({'description': 'В коде есть SQL запрос INSERT с получением данных из внешнего источника и, возможно, выполняется напрямую в БД.', 'status': 'Содержит уязвимость.'})

    if result_UPDATE != None or result_UPDATE_format != None:
        if external_source(decoded_content):
            result_list.append({'description': 'В коде есть SQL запрос UPDATE с получением данных из внешнего источника и, возможно, выполняется напрямую в БД.', 'status': 'Содержит уязвимость.'})

    if result_DELETE != None or result_DELETE_format != None:
        if external_source(decoded_content):
            result_list.append({'description': 'В коде есть SQL запрос SELECT с получением данных из внешнего источника и, возможно, выполняется напрямую в БД.', 'status': 'Содержит уязвимость.'})

    return result_list


def check_pickle(decoded_content, element_unsafe_code):
    result_list = []
    if 'pickle.load(' in decoded_content:
        if external_source(decoded_content):
            result_list.append({'description': element_unsafe_code['add_description'], 'status': 'Содержит уязвимость.'})
        else:
            result_list.append({'description': element_unsafe_code['description'], 'status': element_unsafe_code['status']})

    return result_list


def check_django_email(decoded_content, element_unsafe_code, name_module):
    result_list = []
    if name_module =='settings.py':
        if f'{element_unsafe_code["string_code"]} =' in decoded_content:
            result_list.append({'description': element_unsafe_code['description'], 'status': element_unsafe_code['status']})

    return result_list


def write_results(item, danger_modules_describe, element_unsafe_code, session):
    '''
    Записываем результат поиска в словарь
    :return: словарь
    '''
    # Если есть модуль не проходит доп. проверку, то берем ошибку из доп. проверки
    html_url = f'https://api.github.com/repos/{item["repository"]["full_name"]}/contents/{item["path"]}'

    file_response = session.get(html_url)
    decoded_content = base64.b64decode(file_response.json()['content']).decode('utf-8')

    result_check_list = []
    if element_unsafe_code['string_code'] == 'eval':
        result_check_list = check_eval(decoded_content, element_unsafe_code)
    elif element_unsafe_code['string_code'] == 'sqlite3':
        result_check_list = check_SQL(decoded_content)
    elif element_unsafe_code['string_code'] == 'pickle':
        result_check_list = check_pickle(decoded_content, element_unsafe_code)
    elif element_unsafe_code['string_code'] == 'EMAIL_HOST_USER' or element_unsafe_code['string_code'] == 'EMAIL_HOST_PASSWORD':
        result_check_list = check_django_email(decoded_content, element_unsafe_code, item['name'])

    # Получаем данные для вывода
    for result_check in result_check_list:
        repository_url = item['repository']['html_url']
        language = element_unsafe_code['language']
        name_module = item['name']
        description = result_check['description']
        status = result_check['status']
        url_module = item['html_url']
        #pprint.pprint(item)

        unsafe_modules = {'name_module': name_module, 'description': description, 'status': status, 'url_module': url_module}

        if repository_url in danger_modules_describe:
            if not (language in danger_modules_describe[repository_url]['languages']):
                danger_modules_describe[repository_url]['languages'].append(language)
            danger_modules_describe[repository_url]['unsafe_modules'].append(unsafe_modules)
        else:
            danger_modules_describe[repository_url] = {'languages': [language], 'unsafe_modules' : [unsafe_modules]}

    return danger_modules_describe


def write_json(danger_modules_describe):
    '''
    Записываем результат поиска в файл JSON
    :param danger_modules_describe: словарь
    '''
    with open('danger_modules_GitHub.json', 'w', encoding='utf-8') as f:
        json.dump(danger_modules_describe, f, ensure_ascii=False)
        pprint.pprint(danger_modules_describe)


def dict_to_str(dict):
    '''
    Для записи в БД преобразуем словарь в строку с разделителями |
    :param dict: словарь
    :return: строка
    '''
    result = ''
    for item in dict.items():
        result = f'{result}|{item}'
    return result


def dict_from_str(s):
    '''
    Получаем из строки словарь
    :param s: строка
    :return: словарь
    '''
    result = {}
    for item in s.split('|'):
        if item:
            result[item.split("'")[1]] = item.split("'")[3]
    return result


def write_to_base(danger_modules_describe, user_settings):
    '''
    Записываем результат в БД
    :param danger_modules_describe: словарь с опасным кодом
    :param user_settings: настройки пользователя
    '''
    conn, cursor = get_cursor()
    cursor.execute("insert into History (date, params) VALUES (?, ?)", (datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), dict_to_str(user_settings)))
    id_history = cursor.lastrowid

    for item in danger_modules_describe.items():
        cursor.execute("insert into History_repositories (history, repository, language) VALUES (?, ?, ?)", (id_history, item[0], item[1]['languages'][0]))
        id_history_repositories = cursor.lastrowid

        for item_unsafe_modules in item[1]['unsafe_modules']:
            cursor.execute("insert into History_unsafe_code (repository, unsafe_code) VALUES (?, ?)", (id_history_repositories, dict_to_str(item_unsafe_modules)))

    conn.commit()
    conn.close()


def get_history_list(id=None):
    '''
    Получаем из БД Историю поиска
    :param id: идентификатор записи
    :return: список
    '''
    conn, cursor = get_cursor()
    if id:
        cursor.execute('SELECT * FROM History WHERE id=?', (id,))
    else:
        cursor.execute('SELECT * FROM History')
    result_query = cursor.fetchall()

    result = []
    for item in result_query:
        param_list = []
        repository = ''
        for param in item[2].split('|'):
            if param:
                string_code = param.split("'")[1]
                if string_code == 'repository_name':
                    repository = param.split("'")[3]
                else:
                    cursor.execute('SELECT description from Unsafe_codes WHERE string_code=?', (string_code,))
                    result_description = cursor.fetchall()
                    param_list.append(result_description[0][0])

        result.append({'id': item[0],
                  'date': item[1],
                  'repository': repository,
                  'params': param_list})

    conn.close()
    return result


def get_danger_modules_describe(id):
    '''
    Получаем из БД опасный код для истории поиска
    :param id: идентификатор записи
    :return: словарь
    '''
    conn, cursor = get_cursor()
    cursor.execute('SELECT id, repository, language FROM History_repositories WHERE history=?', (id,))
    result_repository = cursor.fetchall()
    danger_modules_describe = {}
    for item_repository in result_repository:
        cursor.execute('SELECT unsafe_code FROM History_unsafe_code WHERE repository=?', (item_repository[0],))
        result_unsafe_code = cursor.fetchall()
        list_unsafe_code = []
        for item_unsafe_code in result_unsafe_code:
            list_unsafe_code.append(dict_from_str(item_unsafe_code[0]))

        danger_modules_describe[item_repository[1]] = {'languages': [item_repository[2]], 'unsafe_modules': list_unsafe_code}
        #print(danger_modules_describe)
    conn.close()
    return danger_modules_describe


def seaching_unsafe_code(user_settings, PROGRAM_SETTINGS):
    '''
    Поиск опасного кода
    :param user_settings: настройки пользователя
    :param PROGRAM_SETTINGS: настройки программы
    :return: словарь
    '''
    #Загружаем токен из файла
    token = load_token(PROGRAM_SETTINGS['path_to_token'])
    session = requests.Session()
    session.auth = ('DmiFomin', token)

    unsafe_code = PROGRAM_SETTINGS['unsafe_codes']
    danger_modules_describe = {}

    repository_name = user_settings['repository_name']

    for element_unsafe_code in unsafe_code:
        if not (element_unsafe_code['string_code'] in user_settings):
            continue

        string_languages = f'language:{element_unsafe_code["language"]}'
        string_searching = element_unsafe_code["string_code"]

        #print('--------------------------- Ищем', string_searching, 'в модулях на', string_languages, '---------------------------')
        #string_connect = f'https://api.github.com/search/code?q={string_searching}in:file+{string_languages}+user:DanteOnline'
        #string_connect = f'https://api.github.com/search/code?q={string_searching}in:file+{string_languages}page=20&per_page=100{f"+user:{repository_name}" if repository_name else ""}'
        string_connect = f'https://api.github.com/search/code?q={string_searching}in:file+{string_languages}{f"+user:{repository_name}" if repository_name else ""}'
        #print(string_connect)
        try:
            result = session.get(string_connect)
            #print(result.status_code)
            items = result.json()['items']

            for item in items:
                if not item['path'].startswith('venv'):
                    danger_modules_describe = write_results(item, danger_modules_describe, element_unsafe_code, session)

        except Exception as e:
            print(e)


    #write_json(danger_modules_describe)
    write_to_base(danger_modules_describe, user_settings)
    return danger_modules_describe

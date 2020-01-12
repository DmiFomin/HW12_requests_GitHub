import os
import json
import pprint
import base64
import re


def get_program_settings():
    """
    Получаем настройки программы
    :return: Возвращаем словарь с настройками
    """
    # TODO возможно стоит сделать загрузку из файла
    unsafe_codes = [{'language': 'python', 'string_code': 'eval', 'description': 'В коде есть функция eval.',  'add_description': 'В функцию eval, возможно, передано значение из внешнего источника.', 'status': 'Потенциально опасен'},
                    {'language': 'python', 'string_code': 'sqlite3', 'description': 'В коде есть sql инъекция.', 'add_description': '', 'status': 'Содержит уязвимость'},
                    {'language': 'python', 'string_code': 'pickle', 'description': 'В коде используется модуль pickle.', 'add_description': 'В функцию pickle.load(), возможно, передаются данные из стороннего источника.', 'status': 'Потенциально опасен'},
                    {'language': 'python', 'string_code': 'EMAIL_HOST_USER', 'description': 'Явно указан email.', 'add_description': '', 'status': 'Содержит уязвимость'},
                    {'language': 'python', 'string_code': 'EMAIL_HOST_PASSWORD', 'description': 'Явно указаны пароли от email.', 'add_description': '', 'status': 'Содержит уязвимость'}
                   ]

    program_settings = {'path_to_token': os.path.join(os.getcwd(), 'GitHub_Token'), 'unsafe_codes': unsafe_codes}
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

        unsafe_modules = {'name_module': name_module, 'description': description, 'status': status}

        if repository_url in danger_modules_describe:
            if not (language in danger_modules_describe[repository_url]['languages']):
                danger_modules_describe[repository_url]['languages'].append(language)
            danger_modules_describe[repository_url]['unsafe_modules'].append(unsafe_modules)
        else:
            danger_modules_describe[repository_url] = {'languages': [language], 'unsafe_modules' : [unsafe_modules]}

    return danger_modules_describe


def write_json(danger_modules_describe):
    #pprint.pprint(danger_modules_describe)

    with open('danger_modules_GitHub.json', 'w', encoding='utf-8') as f:
        json.dump(danger_modules_describe, f, ensure_ascii=False)
        pprint.pprint(danger_modules_describe)
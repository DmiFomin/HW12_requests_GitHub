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
    unsafe_codes = [{'language': 'python', 'string_code': 'eval', 'description': 'В коде есть функция eval',
                    'status': 'Потенциально опасен', 'extra_check': True},
                    {'language': 'python', 'string_code': 'SELECT', 'description': 'В коде есть sql инъекция SELECT', 'status': 'Потенциально опасен', 'extra_check': True},
                    {'language': 'python', 'string_code': 'INPUT', 'description': 'В коде есть sql инъекция INPUT', 'status': 'Потенциально опасен', 'extra_check': True},
                    {'language': 'python', 'string_code': 'UPDATE', 'description': 'В коде есть sql инъекция UPDATE', 'status': 'Потенциально опасен', 'extra_check': True},
                    {'language': 'python', 'string_code': 'DELETE', 'description': 'В коде есть sql инъекция DELETE', 'status': 'Потенциально опасен', 'extra_check': True}
                   # {'language': 'python', 'string_code': 'pickle', 'description': 'В коде используется модуль pickle', 'status': 'Потенциально опасен'},
                   # {'language': 'python', 'string_code': 'login', 'description': 'В коде возможно указан логин', 'status': 'Содержит уязвимость'},
                   # {'language': 'python', 'string_code': 'password', 'description': 'В коде возможно указан пароль', 'status': 'Содержит уязвимость'},
                   # {'language': 'django', 'string_code': 'EMAIL_HOST_USER', 'description': 'Явно указаны пароли от email', 'status': 'Содержит уязвимость'},
                   # {'language': 'django', 'string_code': 'EMAIL_HOST_PASSWORD', 'description': 'Явно указаны пароли от email', 'status': 'Содержит уязвимость'},
                   # {'language': 'django', 'string_code': '@csrf_exempt', 'description': 'Локально отключен csrf token', 'status': 'Потенциально опасен'}
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


# Решил для каждой проверки сделать свою функцию.
def check_eval(decoded_content, element_unsafe_code, session):

    result = {}
    if 'eval(' in decoded_content:
        if '.read()' in decoded_content or 'input' in decoded_content:
            result['description'] = 'В функцию eval, возможно, передано значение из внешнего источника.'
            result['status'] = 'Содержит уязвимость.'
        else:
            result['description'] = element_unsafe_code['description']
            result['status'] = element_unsafe_code['status']\

    return result


def check_SQL(decoded_content, element_unsafe_code, session):
    regular_str = 'f"{} SELECT {} FROM'

    match = re.search(r'\d\d\D\d\d', r'Телефон 123-12-12')
    print(match[0] if match else 'Not found')



def write_results(item, danger_modules_describe, element_unsafe_code, session):
    # Если есть модуль не проходит доп. проверку, то берем ошибку из доп. проверки
    html_url = f'https://api.github.com/repos/{item["repository"]["full_name"]}/contents/{item["path"]}'

    file_response = session.get(html_url)
    decoded_content = base64.b64decode(file_response.json()['content']).decode('utf-8')

    result_check = {}
    if element_unsafe_code['string_code'] == 'eval':
        result_check = check_eval(decoded_content, element_unsafe_code, session)
    elif element_unsafe_code['string_code'] in ['SELECT', 'INPUT', 'UPDATE', 'DELETE']:
        result_check = check_SQL(decoded_content, element_unsafe_code, session)

    # Получаем данные для вывода
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
import functions as fn
import requests
import pprint

# Записываем настройки
PROGRAM_SETTINGS = fn.get_program_settings()

# Загружаем токен из файла
token = fn.load_token(PROGRAM_SETTINGS['path_to_token'])
session = requests.Session()
session.auth = ('DmiFomin', token)

unsafe_code = PROGRAM_SETTINGS['unsafe_codes']
danger_modules_describe = {}

string_languages = ''
string_searching = ''
for i, element_unsafe_code in enumerate(unsafe_code):
    string_languages = f'language:{element_unsafe_code["language"]}'
    string_searching = element_unsafe_code["string_code"]

    print('--------------------------- Ищем ', string_searching, ' в модулях на ', string_languages, '---------------------------')

    string_connect = f'https://api.github.com/search/code?q={string_searching}in:file+{string_languages}+user:DanteOnline'
    try:
        result = session.get(string_connect)
        print(result.status_code)
        items = result.json()['items']

        for item in items:
            if not item['path'].startswith('venv'):
                danger_modules_describe = fn.write_results(item, danger_modules_describe, element_unsafe_code, session)

    except Exception as e:
        print(e)


fn.write_json(danger_modules_describe)


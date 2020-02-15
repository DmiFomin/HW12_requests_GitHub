import functions as fn
from flask import Flask, render_template, request

# SQL или ORM sqlalchemy
is_SQLite = False

# Записываем настройки
PROGRAM_SETTINGS = fn.get_program_settings(is_SQLite)
user_settings = {'eval': 'on', 'sqlite3': 'on', 'pickle': 'on', 'EMAIL_HOST_USER': 'on', 'EMAIL_HOST_PASSWORD': 'on'}
contacts_info = {'author': PROGRAM_SETTINGS['author'],
                 'phone': PROGRAM_SETTINGS['phone'],
                 'email': PROGRAM_SETTINGS['email']}

app = Flask(__name__)


@app.route("/")
def run():
    return render_template('index.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'])


@app.route('/index/')
def index():
    return render_template('index.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'])


@app.route('/searching/', methods=['GET'])
def searching():
    #print('GET')
    return render_template('searching.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'], user_settings = user_settings, danger_modules_describe='BeforeSearching')


@app.route('/searching/', methods=['POST'])
def run_post():
    params = request.form
    global user_settings
    user_settings = {}
    #print('POST')
    for param in params:
        if param != 'repository_name':
            user_settings[param] = 'on'
        else:
            user_settings[param] = params['repository_name']

    #print(user_settings)
    danger_modules_describe = fn.seaching_unsafe_code(user_settings, PROGRAM_SETTINGS, is_SQLite)
    return render_template('searching.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'], user_settings = user_settings, danger_modules_describe=danger_modules_describe)


@app.route('/searching_history/', methods=['GET'])
def searching_history():
    history_list = fn.get_history_list(is_SQLite)
    return render_template('searching_history.html', history_list = history_list)


@app.route('/searching_history/', methods=['POST'])
def searching_history_post():
    params = list(request.form)
    history_list = fn.get_history_list(is_SQLite, int(params[0]))
    danger_modules_describe = fn.get_danger_modules_describe(int(params[0]), is_SQLite)
    return render_template('searching_history.html', history_list = history_list, danger_modules_describe=danger_modules_describe)


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html', contacts_info = contacts_info)


if __name__ == "__main__":
    app.run(debug=True)





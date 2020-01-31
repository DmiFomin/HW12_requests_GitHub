import functions as fn
from flask import Flask, render_template, request

# Записываем настройки
PROGRAM_SETTINGS = fn.get_program_settings()
user_settings = {'eval': 'on', 'sqlite3': 'on', 'pickle': 'on', 'EMAIL_HOST_USER': 'on', 'EMAIL_HOST_PASSWORD': 'on', '11':'22'}
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
    print('GET')
    return render_template('searching.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'], user_settings = user_settings, danger_modules_describe='BeforeSearching')


@app.route('/searching/', methods=['POST'])
def run_post():
    params = request.form
    global user_settings
    user_settings = {}
    print('POST')
    for param in params:
        if param != 'repository_name':
            user_settings[param] = 'on'
        else:
            user_settings[param] = params['repository_name']

    print(user_settings)

    # TODO Хотел добавить прогрессбар, но не получилось. Не понял как обновить страницу без return.
    #render_template('searching.html', unsafe_codes=PROGRAM_SETTINGS['unsafe_codes'],  user_settings=user_settings, danger_modules_describe='Searching')
    danger_modules_describe = fn.seaching_unsafe_code(user_settings)
    return render_template('searching.html', unsafe_codes = PROGRAM_SETTINGS['unsafe_codes'], user_settings = user_settings, danger_modules_describe=danger_modules_describe)


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html', contacts_info = contacts_info)


if __name__ == "__main__":
    app.run(debug=True)





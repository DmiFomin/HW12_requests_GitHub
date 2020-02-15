from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime
import utility


engine = create_engine('sqlite:///C:\\Users\\fomin\\DataBases_SQLite\\db_CheckingGitHub_ORM.db?check_same_thread=False', echo=True)
Base = declarative_base()


class Settings(Base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True)
    path_to_token = Column(String)
    author = Column(String)
    phone = Column(String)
    email = Column(String)

    def __init__(self, path_to_token, author, phone, email):
        self.path_to_token = path_to_token
        self.author = author
        self.phone = phone
        self.email = email


class Statuses(Base):
    __tablename__ = 'Statuses'
    id = Column(Integer, primary_key=True)
    description = Column(String)

    unsafe_codes = relationship("Unsafe_codes")

    def __init__(self, description):
        self.description = description


class Unsafe_codes(Base):
    __tablename__ = 'Unsafe_codes'
    id = Column(Integer, primary_key=True)
    language = Column(String)
    string_code = Column(String)
    description = Column(String)
    add_description = Column(String)
    status = Column(Integer, ForeignKey('Statuses.id'))

    statuses = relationship("Statuses")

    def __init__(self, language, string_code, description, add_description, status):
        self.language = language
        self.string_code = string_code
        self.description = description
        self.add_description = add_description
        self.status = status


class History(Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    params = Column(String)

    def __init__(self, date, params):
        self.date = date
        self.params = params


class History_repositories(Base):
    __tablename__ = 'History_repositories'
    id = Column(Integer, primary_key=True)
    history = Column(Integer, ForeignKey('History.id'))
    repository = Column(String)
    language = Column(String)

    def __init__(self, history, repository, language):
        self.history = history
        self.repository = repository
        self.language = language


class History_unsafe_code(Base):
    __tablename__ = 'History_unsafe_code'
    id = Column(Integer, primary_key=True)
    repository = Column(Integer, ForeignKey('History_repositories.id'))
    unsafe_code = Column(String)

    def __init__(self, repository, unsafe_code):
        self.repository = repository
        self.unsafe_code = unsafe_code


Base.metadata.create_all(engine)


def get_program_settings():
    Session = sessionmaker(bind=engine)
    session = Session()

    unsafe_codes = []

    # Получаем список уязвимостей
    result_unsafe_codes = session.query(Unsafe_codes, Statuses).join(Statuses).all()
    for item in result_unsafe_codes:
        unsafe_codes.append({'language': item.Unsafe_codes.language,
                             'string_code': item.Unsafe_codes.string_code,
                             'description': item.Unsafe_codes.description,
                             'add_description': item.Unsafe_codes.add_description if item.Unsafe_codes.add_description != None else '',
                             'status': item.Statuses.description})

    result_settings = session.query(Settings).all()[0]
    program_settings = {'path_to_token': os.path.join(os.getcwd(), result_settings.path_to_token),
                        'unsafe_codes': unsafe_codes,
                        'author': result_settings.author,
                        'phone': result_settings.phone,
                        'email': result_settings.email}

    return program_settings


def add_history(danger_modules_describe, user_settings):
    Session = sessionmaker(bind=engine)
    session = Session()

    history = History(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), utility.dict_to_str(user_settings))
    session.add(history)
    session.commit()
    id_history = history.id

    for item in danger_modules_describe.items():
        history_repositories = History_repositories(id_history, item[0], item[1]['languages'][0])
        session.add(history_repositories)
        session.commit()
        id_history_repositories = history_repositories.id

        for item_unsafe_modules in item[1]['unsafe_modules']:
            history_unsafe_code = History_unsafe_code(id_history_repositories, utility.dict_to_str(item_unsafe_modules))
            session.add(history_unsafe_code)

        session.commit()


def get_history_list(id=None):
    Session = sessionmaker(bind=engine)
    session = Session()

    if id:
        result_query = session.query(History).filter(History.id == id).all()
    else:
        result_query = session.query(History).all()

    result = []
    for item in result_query:
        param_list = []
        repository = ''
        for param in item.params.split('|'):
            if param:
                string_code = param.split("'")[1]
                if string_code == 'repository_name':
                    repository = param.split("'")[3]
                else:
                    result_description = session.query(Unsafe_codes).filter(Unsafe_codes.string_code == string_code).first()
                    param_list.append(result_description.description)

        result.append({'id': item.id,
                       'date': item.date,
                       'repository': repository,
                       'params': param_list})

    return result


def get_danger_modules_describe(id):
    print('ORM')
    print(id)
    Session = sessionmaker(bind=engine)
    session = Session()

    result_repository = session.query(History_repositories).filter(History_repositories.history == id)
    danger_modules_describe = {}
    for item_repository in result_repository:
        result_unsafe_code = session.query(History_unsafe_code).filter(History_unsafe_code.repository == item_repository.id)
        list_unsafe_code = []
        for item_unsafe_code in result_unsafe_code:
            list_unsafe_code.append(utility.dict_from_str(item_unsafe_code.unsafe_code))

        danger_modules_describe[item_repository.repository] = {'languages': [item_repository.language],
                                                               'unsafe_modules': list_unsafe_code}

    return danger_modules_describe
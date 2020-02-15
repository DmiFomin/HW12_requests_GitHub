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
# Поиск уязвимостей в модулях GitHub

Сайт позволяет найти модули, в которых содержатся следующие уязвимости:
* В коде есть функция eval.
* В коде есть sql инъекция.
* В коде используется модуль pickle.
* Явно указан email.
* Явно указаны пароли от email.

Так же можно указать имя пользователя GiHub для поиска в конкретном репозитории. Если имя не указывать, то поиск будет ограничен 2000 репозиториями для кадого типа уязвимости.

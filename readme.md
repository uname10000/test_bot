**Стэк технологий**
1) Python3
2) MongoDB
3) MongoEngine
4) Flask
5) Flask restful
6) Telebot
7) Google cloud
8) Nginx
9) Gunicorn
10) Marshmallow


**Сущности бд**
1) Продукты
   1. Название
   2. Описание
   3. {Категория}
   4. Цена
   5. Наличие
   6. Картинка
   7. Скидка в процентах
2) Категории
   1. Название категории
   2. Описание категории
   3. {parent}
   4. [{подкатегории}]
3) Пользователи
   1. telegram id (ПК)
   2. Номер телефона
   3. Никнейм
4) Корзина
5) Заказы
6) Новости
   1. Заголовок
   2. Содержимое
   3. Дата публикации
   

# Lesson 12
1) Создать абстрактную коллекцию. Она должна содержать два поля created & modified, и хранить в них дату и время.
created - время создания объекта, modified - время последнего обновления. Логику со временем размещаем в методе save.
2) Проиницианализировать бот. Описать хендлер /start.
   При старте приветствовать пользователя. Создать модуль constants, в котором будут константно хранится текста и другие константы
   
# Lesson 13
1) Описать хендлер, который будет отрабатывать при клике на кнопку "новости". Выводить последние 5 новостей
2) Коллекция новостей должна наследовать абстрактную коллекцию (created_at, modified_at, 12.1)
3) Описать хендлер для клика на кнопку определенной категории. Выводить название всех продуктов, которые относятся к кликнутой категории
   Названия продуктов выводить отдельными сообщениями.
   
# Lesson 14
1) Описать метод форматирования описание продуктов (цена с учетом скидки (метод сделали на занятии), название, описание, характеристики)
отправлять эту информацию под картинкой продукта
2) Описать хендлер для обработки кликов на категории (Сделано на занятии)
3) Описать колекцию корзины и заказов

# Lesson 15
1) Реализовать логику для изменения данных профиля (почта, номер телефона, имя, адрес).
   Добавить в модель юзера поле адрес
   
# Lesson 16
1) Нужно создать акаутн на google cloude, создать виртуальную машину (1 vcp, 1GB mem, 40Gb Hdd)
2) Рассылка сообщений (сделали на занятии)
3) Вывод содержимого корзины. При клике на кнопку "Корзина", пользователю должно выводится все содержимое с возможностью увеличить либо уменьшить количество
4) Оформление заказа. В момент формирования корзины добавить кнопку "Завершить заказ". После нажатия на кнопку завершить заказ, выводить пользователю все, что он добавл в корзину. Заросить у него данные ( почта, номер телефона, адрес )
5) После создания новости в БД, отправлять ее всем пользователям бота

# Lesson 17
1) Создать REST (в пакете api). REST API должен покрывать следующие модели: новости, пользователи, заказы (чтение),
продукты, категории. Посмотреть в сторону blueprint для flask (решит запрос с созданием доп объекта app).
Используем flask_restful
   
Обязательным условием защиты проекта:
1) Размещение на сервере
2) REST API
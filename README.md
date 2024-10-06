# SysAdminBot
**SysAdminBo** - бот для Telegram, который позволяет взаимодействовать с удаленными серверами через SSH и выполнять команды для сбора системной информации, мониторинга состояния сервера, а также другие операции.

## Возможности
* Получение информации о системе (uptime, df, free и т.д.)
* Сбор информации об установленных пакетах (apt)
* Просмотр сетевых соединений (ss)
* Поиск телефонных номеров и email-адресов в тексте
* Проверка сложности паролей
* Логи выполнения команд
## Установка
1. Клонируйте репозиторий:
```git clone https://github.com/kirillivanv/SysAdminBot.git ```
2. Установите необходимые библиотеки:
```pip install -r requirements.txt```
3. Создайте файл .env с переменными окружения:
```
* TOKEN = "your_token"
* HOST = your_ssh_host
* PORT = your_ssh_port
* USER = your_ssh_user
* PASSWORD = your_ssh_password
```
4. Запустите бота
## Использование
**Поиск информации в тексте и вывод ее**
Информация, которую бот умеет выделять из текста: 
* Email-адреса. 
Команда: ```/find_email```
* Номера телефонов. 
Команда: ```/find_phone_number```

import logging
import re
import paramiko
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    filename='logfile.txt', 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

logger = logging.getLogger(__name__)

PASSWORD_STATE = 'passwordState'

# SSH connection 
SSH_HOST = os.getenv("HOST")
SSH_PORT = int(os.getenv("PORT"))
SSH_USERNAME = os.getenv("USER")
SSH_PASSWORD = os.getenv("PASSWORD")

def ssh_command(command: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD)
    stdin, stdout, stderr = client.exec_command(command)
    result = stdout.read().decode('utf-8')
    client.close()
    return result

# Команды для сбора информации о системе
def get_release(update: Update, context: CallbackContext):
    result = ssh_command("cat /etc/*-release")
    update.message.reply_text(result)
    logger.info('Command /get_release executed.')

def get_uname(update: Update, context: CallbackContext):
    result = ssh_command("uname -a")
    update.message.reply_text(result)
    logger.info('Command /get_uname executed.')

def get_uptime(update: Update, context: CallbackContext):
    result = ssh_command("uptime")
    update.message.reply_text(result)
    logger.info('Command /get_uptime executed.')

def get_df(update: Update, context: CallbackContext):
    result = ssh_command("df -h")
    update.message.reply_text(result)
    logger.info('Command /get_df executed.')

def get_free(update: Update, context: CallbackContext):
    result = ssh_command("free -m")
    update.message.reply_text(result)
    logger.info('Command /get_free executed.')

def get_mpstat(update: Update, context: CallbackContext):
    result = ssh_command("mpstat")
    update.message.reply_text(result)
    logger.info('Command /get_mpstat executed.')

def get_w(update: Update, context: CallbackContext):
    result = ssh_command("w")
    update.message.reply_text(result)
    logger.info('Command /get_w executed.')

def get_auths(update: Update, context: CallbackContext):
    result = ssh_command("last -n 10")
    update.message.reply_text(result)
    logger.info('Command /get_auths executed.')

def get_critical(update: Update, context: CallbackContext):
    result = ssh_command("journalctl -p crit -n 5")
    update.message.reply_text(result)
    logger.info('Command /get_critical executed.')

def get_ps(update: Update, context: CallbackContext):
    result = ssh_command("ps aux")
    with open("ps.txt", "w") as file:
        file.write(result)
    with open("ps.txt", "rb") as file:
        update.message.reply_document(document=file)
    logger.info('Command /get_ps executed.')


def get_ss(update: Update, context: CallbackContext):
    result = ssh_command("ss -tuln")
    update.message.reply_text(result)
    logger.info('Command /get_ss executed.')

def get_apt_list(update: Update, context: CallbackContext):
    # Получение аргумента команды, если он был передан
    package_name = " ".join(context.args)
    if package_name:
        # Если было передано название пакета, выполнить поиск информации о нем
        result = ssh_command(f"apt show {package_name}")
    else:
        # В противном случае вывести список всех установленных пакетов
        result = ssh_command("apt list --installed")
    
    # Отправка результата пользователю
    with open("apt_list.txt", "w") as file:
        file.write(result)
    with open("apt_list.txt", "rb") as file:
        update.message.reply_document(document=file)
    
    logger.info('Command /get_apt_list executed.')

def get_services(update: Update, context: CallbackContext):
    result = ssh_command("systemctl list-units --type=service")
    with open("service_list.txt", "w", encoding="utf-8") as file:
        file.write(result)
    with open("service_list.txt", "rb") as file:
        update.message.reply_document(document=file)
    logger.info('Command /get_services executed.')

# Основные команды
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    logger.info(f'User {user.full_name} started the bot.')

def helpCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')
    logger.info('Help command issued.')

# Обработка команды для поиска телефонных номеров
def findPhoneNumbersCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска телефонных номеров:')
    logger.info('Phone number search command issued.')
    return 'findPhoneNumbers'

# Поиск телефонных номеров
def findPhoneNumbers(update: Update, context: CallbackContext):
    user_input = update.message.text
    logger.info(f'User input for phone number search: {user_input}')
    phoneNumRegex = re.compile(r'(8|\+7)[-\s]?(\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        logger.info('No phone numbers found.')
    else:
        phoneNumbers = '\n'.join([f'{i+1}. {phone[0]}{phone[1]}' for i, phone in enumerate(phoneNumberList)])
        update.message.reply_text(phoneNumbers)
        logger.info(f'Phone numbers found: {phoneNumbers}')
    return ConversationHandler.END

# Обработка команды для поиска email-адресов
def findEmailCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска email-адресов:')
    logger.info('Email search command issued.')
    return 'findEmails'

# Поиск email-адресов
def findEmails(update: Update, context: CallbackContext):
    user_input = update.message.text
    logger.info(f'User input for email search: {user_input}')
    emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        logger.info('No email addresses found.')
    else:
        emails = '\n'.join([f'{i+1}. {email}' for i, email in enumerate(emailList)])
        update.message.reply_text(emails)
        logger.info(f'Email addresses found: {emails}')
    return ConversationHandler.END

# Обработка команды для проверки сложности пароля
def verifyPasswordCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите пароль для проверки:')
    logger.info('Password verification command issued.')
    return PASSWORD_STATE

# Проверка сложности пароля
def verifyPassword(update: Update, context: CallbackContext):
    password = update.message.text
    logger.info(f'User input for password verification: {password}')
    password_regex = re.compile(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )
    if password_regex.match(password):
        update.message.reply_text('Пароль сложный')
        logger.info('Password is strong.')
    else:
        update.message.reply_text('Пароль простой')
        logger.info('Password is weak.')
    return ConversationHandler.END

# Обработка произвольных сообщений (эхо)
def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)
    logger.info(f'Echo message: {update.message.text}')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики для поиска телефонных номеров
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    # Обработчики для поиска email-адресов
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
        },
        fallbacks=[]
    )

    # Обработчики для проверки сложности пароля
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            PASSWORD_STATE: [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))

    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_services", get_services))

    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

build_guides_server = 'https://wiki.lineageos.org'
device_list_server = build_guides_server + '/build_guides.html'
device_list_tag = 'a'
device_list_splitter = 'href="'
device_list_part_a = '/devices/'
device_list_part_b = '/build'
search_limit = 5
readme_char_limit = 250
repo_url = 'https://github.com/FacuM/romdeliverybot_support'
bot_name = 'Robbie'
general_error = 'Sorry, I can\'t help you with that right now.\n\nHowever, if you find the solution by yourself, it\'d be great if you could create a pull request in my [source code](https://github.com/FacuM/romdeliverybot_support).'
critical_error = 'Sorry, there was a critical problem and my brain stopped working (so my dev\'s), you might want to [create an issue](' + repo_url + '/issues/new).'
bot_name_lower = bot_name.lower()

try:
    print('Importing "os"...')
    import os
    print('Successfully imported "os"!')
    print('Importing "logging"...')
    import logging
    print('Successfully imported "logging"!')
    print('Importing "telebot"...')
    import telebot
    print('Successfully imported "telebot"!')
    print('Importing "HTMLParser" from "html.parser"...')
    from html.parser import HTMLParser
    print('Successfully imported "HTMLParser"!')
    print('Importing "requests"...')
    import requests
    print('Successfully imported "requests"!')
    print('Importing "Github"...')
    from github import Github
    print('Successfully imported "github"!')
    print('Importing "base64"...')
    import base64
    print('Successfully imported "base64"!')
    print('Importing "time"...')
    import time
    print('Successfully imported "time"!')
    print('Importing "PyMySQL"...')
    import pymysql
    print('Successfully imported "PyMySQL"!')
    print('Importing "duckduckgo"...')
    import duckduckgo
    print('Successfully imported "duckduckgo"!')
    print('Importing "mistune"...')
    import mistune
    print('Successfully imported "mistune"!')
    print('Importing "re" (regular expressions)...')
    import re
    print('Successfully imported "re"!')
except ImportError:
    print('Failed to import required modules, quitting...')
    exit(1)

def clear(n):
    for i in range(n):
        print('\n')

def warn_sleep():
    time.sleep(1.5)

def print_important(msg):
    def print_separator(char_amount):
        for i in range(char_amount):
            print('=', end='')
        print('')

    max_len = 0
    for line in msg.splitlines():
        if (len(line) > max_len):
            max_len = len(line)

    clear(5)
    print_separator(max_len)
    print(msg)
    print_separator(max_len)
    clear(5)

def get_plaintext(html):
    processed = html.replace('<br>', '\n')
    ret = ''
    for line in processed.splitlines():
        ret += re.sub('</?[^>]+>', '', line) + '\n'
    return ret

def main():
    database_available = True

    print_important('Hello! My name is ' + bot_name + ' and I\'m not very smart.\n' +
                    '\n' +
                    'I\'m written in Python but I don\'t rely on any AI.\n' +
                    'Please be kind with me. :)\n' +
                    'Starting...')

    def get_environment(value, message, required=False, db=False):
        ret = os.environ.get(value, '')
        if (not ret):
            if (required):
                print ('Missing ' + message + ', please set the environment variable ' + value)
                exit(1)
            else:
                if (db):
                    print('Missing ' + message + ', all GitHub-related modules will be disabled.')
                    nonlocal database_available
                    database_available = False
                else:
                    print('Missing ' + message + ', this could cause some issues.')
                warn_sleep()
        else:
            return ret

    # Try to set up the API_KEY, if it's not present, crash.
    api_key = get_environment(value='API_KEY', message='API key', required=True)

    mysql_hostname = get_environment(value='MYSQL_HOSTNAME', message='MySQL server hostname', db=True)

    mysql_username = get_environment(value='MYSQL_USERNAME', message='MySQL server username', db=True)

    mysql_password = get_environment(value='MYSQL_PASSWORD', message='MySQL server password', db=True)

    mysql_dbname = get_environment(value='MYSQL_DBNAME', message='MySQL database name', db=True)

    mysql_table_tokens = bot_name_lower + '_tokens'

    mysql_table_log = bot_name_lower + '_log'

    '''
        Declare the DB object as global, as we're gonna write to it at least
        once.

        TODO: There must be a better solution, improve the underlying code.
    '''
    db = None
    def connect_mysql(retrying=False):
        try:
            nonlocal db
            if (retrying):
                # Retry DB connection.
                print('Retrying to connect to the MySQL server...')
                try:
                    db.close()
                except:
                    pass
            else:
                # Test DB connection.
                print('Connecting to the MySQL server...')
            db = pymysql.connect(host=mysql_hostname, user=mysql_username, password=mysql_password, db=mysql_dbname)
            print('Success connecting to the MySQL server!')
        except:
            print('Failed to connect to the MySQL server, all GitHub-related modules will be disabled.')
            database_available = False
            warn_sleep()
    connect_mysql()

    def populate_database():
        try:
            cur = db.cursor()
            cur.execute('SHOW TABLES')
            result = cur.fetchall()
            tables = []
            for table in result:
                tables.append(table[0])
            if (not (mysql_table_tokens in tables)):
                # Try to create the table (if not existing).
                print('Creating table "' + mysql_table_tokens + '"...')
                cur = db.cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS `' + mysql_table_tokens + '` (chat_id int(11) NOT NULL, token varchar(40) NOT NULL , PRIMARY KEY (`chat_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8')
                cur.close()
                db.commit()
            if (not (mysql_table_log in tables)):
                # Try to create the table (if not existing).
                print('Creating table "' + mysql_table_log + '"...')
                cur = db.cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS `' + mysql_table_log + '` ( `message_id` INT NOT NULL , `chat_id` INT NOT NULL , `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`message_id`)) ENGINE = InnoDB')
                cur.close()
                db.commit()
        except:
            pass
    populate_database()

    def log_operation(operation, message=None, message_id=None, chat_id=None, status=False):
        log = operation.upper() + ': message_id=' + str(message_id) + ', chat_id=' + str(chat_id) + ', status='
        if ((message_id is None) or (chat_id is None)):
            log = operation.upper() + ': message_id=' + str(message.message_id) + ', chat_id=' + str(message.chat.id) + ', status='
        else:
            log = operation.upper() + ': message_id=' + str(message_id) + ', chat_id=' + str(chat_id) + ', status='
        log += str(status)
        print(log)

    def log_message(message):
        # If a database is available, log messages once received.
        if (database_available):
            try:
                cur = db.cursor()
                cur.execute('INSERT INTO ' + mysql_table_log + ' (chat_id, message_id) VALUES (%s, %s)', (message.chat.id, message.message_id))
                cur.close()
                db.commit()
                log_operation(operation='TRACK_MESSAGE', message=message, status=True)
            except (pymysql.err.Error, AttributeError) as e:
                log_operation(operation='TRACK_MESSAGE', message=message, status=False)
                print(str(e))
                connect_mysql(retrying=True)
        return message

    print('Parsing provided device list...') # LineageOS by default, customize.
    parser = HTMLParser()
    build_guides = []

    # Try to get the list (only if possible).
    try:
        device_list = requests.get(device_list_server)
        if (device_list.status_code == 200):
            print('Success loading device list from server!')
            device_list = device_list.content
            pre = ''
            # Pass the output from the request response in device_list
            print('Parsing data...')

            for char in str(device_list):
                parser.feed(char)
                cur = parser.get_starttag_text()
                if ('build' in str(cur) and pre != cur):
                    build_guides.append(str(cur).split(device_list_splitter)[1].replace(device_list_part_a, '').replace(device_list_part_b, ''))
                pre = cur
            for i in range(len(build_guides)):
                build_guides[i] = build_guides[i].replace('">', '')

            print('Done parsing!')
        else:
            print('Failed to parse device list!')
    except:
        pass

    print_important('Startup complete!')

    bot = telebot.TeleBot(api_key)
    bot_user_id = bot.get_me().id

    logger = telebot.logger
    telebot.logger.setLevel(logging.WARN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        log_message(bot.reply_to(message, "Hey, what's up? To learn how to use me, type /help."))

    @bot.message_handler(commands=['help'])
    def send_help(message):
        log_message(bot.reply_to(message, "Using me is pretty simple, just type your query and I'll try to find it through my code!"))

    @bot.message_handler(func=lambda i:True)
    def everything(message):
        log_message(message)
        content = str(message.text).lower().replace('?', '').replace('¿', '')
        try:
            message_replied = message.reply_to_message.from_user.id
        except:
            message_replied = None
        group_call = ( (message.chat.type == 'group' or message.chat.type == 'supergroup') and ( (bot_name_lower in content) or (message_replied == bot_user_id) ) )
        if ( (message.chat.type == 'private') or (group_call) ):
            if ("build" in content):
                log_operation(operation='GUIDE_REQUEST_BEGIN', message=message, status=True)
                if ("twrp" in content):
                    log_message(bot.reply_to(message, "For a basic introduction, check this [XDA thread](https://forum.xda-developers.com/showthread.php?t=1943625).", parse_mode='Markdown'))
                elif ("android" in content):
                    device_index = -1
                    if (len(build_guides) > 0):
                        for word in content.replace('build', '').replace('android', '').split():
                            try:
                                device_index = build_guides.index(word)
                                break
                            except ValueError:
                                pass
                    if (device_index > -1):
                        log_message(bot.reply_to(message, "I found a guide for your device, get it here: [build guide for " + build_guides[device_index] + "](" +  build_guides_server + device_list_part_a + build_guides[device_index] + device_list_part_b + ").", parse_mode='Markdown'))
                    else:
                        log_message(bot.reply_to(message, "A great guide to follow about this topic is the one from LineageOS, you can [check it out here](" + device_list_server + ").\n\nYou can also ask me about your specific device's build guide!", parse_mode='Markdown'))

                    log_operation(operation='GUIDE_REQUEST', message=message, status=True)
                else:
                    log_operation(operation='GUIDE_REQUEST', message=message, status=False)
                    log_message(bot.reply_to(message, general_error, parse_mode='Markdown'))
                log_operation(operation='GUIDE_REQUEST_END', message=message, status=True)

            elif ( ('my' in content) and ('github' in content) and ('username is' in content) and ('password is' in content) ):
                log_operation('GITHUB_LOGIN_BEGIN', message, status=True)
                message_snapshot = message

                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except:
                    log_message(bot.reply_to(message, 'I couldn\'t remove the message with your credentials from this chat, please delete it manually.'))

                try:
                    cur = db.cursor()
                    cur.execute("SELECT COUNT(chat_id) FROM " + mysql_table_tokens + ' WHERE chat_id = %s', (message_snapshot.from_user.id,)) # make a tuple and escape
                    token_count = cur.fetchone()[0]

                    cur.close()
                    db.commit() # try to commit (if possible)

                    if (token_count > 0):
                        log_message(bot.send_message(message_snapshot.chat.id, "I know your token, please type in your search or revoke it."))
                    else:
                        if (group_call):
                            log_message(bot.send_message(message_snapshot.chat.id, 'Sorry, but you\'ll need to send me a private message to use that feature, it wouldn\'t be safe here.'))
                        else:
                            log_message(bot.send_message(message_snapshot.chat.id, "Fine, let me see if it works..."))

                            try:
                                # Parse username.
                                username = message_snapshot.text[content.index("username is"):]
                                username = username.split()[2]

                                # Parse password.
                                password = message_snapshot.text[content.index("pas"):]
                                password = password[password.index("is"):]
                                password = password.split()[1]
                            except:
                                pass

                            g = Github(username, password)

                            try:
                                g.get_user()

                                u = g.get_user()

                                cur = db.cursor()

                                can_authorize = True

                                for auth in u.get_authorizations():
                                    if (auth.note == bot_name):
                                        can_authorize = False
                                        break

                                if (can_authorize):
                                    token = u.create_authorization(note=bot_name).token

                                    cur.execute("INSERT INTO " + mysql_table_tokens + " (chat_id, token) VALUES (%s, %s)", (message_snapshot.from_user.id, token,))
                                    cur.close()
                                    db.commit() # try to commit (if possible)
                                    log_message(bot.send_message(message_snapshot.chat.id, "Welcome " + u.name + "! Please type in your search."))
                                    log_operation('GITHUB_LOGIN', message, status=True)
                                else:
                                    log_operation('GITHUB_LOGIN', message, status=False)
                                    log_message(bot.send_message(message_snapshot.chat.id, 'Sorry, I couldn\'t get a token, please delete "' + bot_name + '" manually from your [personal access tokens](https://github.com/settings/tokens).', parse_mode='Markdown'))
                            except:
                                log_operation('GITHUB_LOGIN', message, status=False)
                                log_message(bot.send_message(message_snapshot.chat.id, "Sorry, those credentails aren't valid."))


                except pymysql.err.Error as e:
                    log_operation('CRITICAL_ERROR', message, status=True)
                    print(e)
                    log_message(bot.reply_to(message, critical_error, parse_mode='Markdown'))
                    connect_mysql(retrying=True)

                log_operation('GITHUB_LOGIN_END', message, status=True)

            elif ( ("github" in content) and ( not( 'duck' in content) or ('duckduckgo' in content) ) ):
                if (database_available):
                    log_operation('GITHUB_SEARCH_BEGIN', message, status=True)
                    if (" search" in content):
                        try:
                            if ("user" in content):
                                log_message(bot.reply_to(message, "Oops... that's not implemented."))
                            else:
                                # If after wiping out the request, the query is empty, report it and quit.
                                query = content.replace('github', '', 1).replace('hey', '').split("search")[1]
                                if (len(query) < 1):
                                    log_message(bot.reply_to(message, "Eh... I guess you should search something."))
                                else:
                                    cur = db.cursor()
                                    cur.execute("SELECT (SELECT COUNT(chat_id) FROM " + mysql_table_tokens + ' WHERE chat_id = %s), (SELECT token FROM ' + mysql_table_tokens + ' WHERE chat_id = %s)', (message.from_user.id, message.from_user.id,))
                                    result = cur.fetchone()
                                    token_count = result[0]
                                    token = result[1]

                                    cur.close()

                                    if (token_count < 1):
                                        log_message(bot.reply_to(message, 'Sorry, I don\'t know you. Please tell me both your GitHub username and password.', parse_mode='Markdown'))
                                    else:
                                        out_messages = []

                                        loading_message = log_message(bot.send_message(message.chat.id, 'Please wait...'))
                                        bot.send_chat_action(message.chat.id, 'typing')

                                        g = Github(token)

                                        cnt = 0
                                        try:
                                            for repo in g.search_repositories(query=query):
                                                if (cnt < search_limit):
                                                    out =  '✏ Repository: [' + repo.name + '](' + repo.html_url + ')\n'
                                                    out += '👨‍✈️ Owner: [' + repo.owner.login + '](' + repo.owner.html_url + ')\n'
                                                    full_repo = g.get_repo(repo.full_name)
                                                    out += '📜 Topics: '
                                                    topics = full_repo.get_topics()
                                                    if (len(topics) > 0):
                                                        for topic in full_repo.get_topics():
                                                            out += '#' + topic + ' '
                                                    else:
                                                        out += ' no topics.'
                                                    out += '\n'
                                                    out += '👨‍💻 Forks: ' + str(full_repo.forks_count) + '\n'
                                                    out += '⭐ Stars: ' + str(full_repo.stargazers_count) + '\n'
                                                    out += '👀 Watchers: ' + str(full_repo.watchers_count) + '\n'
                                                    out += '\n'
                                                    out += str(repo.description) + '\n'

                                                    # Let's try with each known README type.
                                                    global readme
                                                    readme = ''
                                                    for readme_type in [ '.markdown' , '.md', '' ]:
                                                        try:
                                                            readme = str(base64.b64decode(full_repo.get_contents("README" + readme_type).content), 'utf-8')

                                                            # If found, stop searching.
                                                            break
                                                        except:
                                                            pass

                                                    markdown = mistune.Markdown()

                                                    # If anything is found, lets try to limit it (only if necessary).
                                                    if (len(readme) > 0):

                                                        readme = markdown(readme)

                                                        readme = get_plaintext(readme)

                                                        if (len(readme) > readme_char_limit):
                                                            readme = readme[:readme_char_limit] + '**\[...]**'

                                                        out += '\n' + readme # (len(readme) > 0)

                                                    out_messages.append(out)
                                                    cnt += 1
                                                else:
                                                    break
                                            if (cnt < 1):
                                                out_messages.append('Oops... no results.')
                                            else:
                                                out_messages.append('And... that\'s it! Anything else?')
                                            log_operation('GITHUB_SEARCH', message, status=True)
                                        except:
                                            out_messages.append("Sorry, I couldn\'t process your query.")
                                            log_operation('GITHUB_SEARCH', message, status=False)

                                        # If we're done loading (or failing), delete the loading message.
                                        try:
                                            # Delete it, only if we can. It's not a bad thing though.
                                            bot.delete_message(loading_message.chat.id, loading_message.message_id)
                                        except:
                                            pass

                                        # Now, push the queued messages.
                                        for msg in out_messages:
                                            try:
                                                log_message(bot.send_message(message.chat.id, msg, parse_mode='Markdown'))
                                            except:
                                                pass
                        except pymysql.err.Error as e:
                            log_operation('CRITICAL_ERROR', message, status=True)
                            print(e)
                            log_message(bot.reply_to(message, critical_error, parse_mode='Markdown'))
                            connect_mysql(retrying=True)
                else:
                    log_message(bot.reply_to(message, 'Sorry, but this module is disabled.'))
                log_operation('GITHUB_SEARCH_END', message, status=True)

            elif ( ( ('duckduckgo' in content) or ('duck' in content) ) and ('search' in content) ):
                log_operation('DUCK_SEARCH_BEGIN', message, status=True)
                # If after wiping out the request, the query is empty, report it and quit.
                query = content.replace('duckduckgo', '', 1).replace('duck', '', 1).replace('hey', '').split("search")[1]

                if (len(query) < 1):
                    log_message(bot.reply_to(message, "Eh... I guess you should search something."))
                else:
                    out_messages = []

                    loading_message = log_message(bot.send_message(message.chat.id, 'Please wait...'))
                    bot.send_chat_action(message.chat.id, 'typing')

                    request = duckduckgo.query(query, safesearch=True, html=False)
                    has_results = False

                    try:
                        out = ''
                        # Append the main result.
                        for result in request.results:
                            out += '🔗 Website: [' + result.text + '](' + result.url + ')\n'
                            out += 'ℹ Description: ' + request.abstract.text + '\n'
                            out += '\n'
                            out += 'Source: [' + request.abstract.source + '](' + request.abstract.url + ')'
                            out_messages.append(out)
                            out = ''
                            has_results = True

                        if (has_results):
                            # Append related results.
                            out_messages.append('🔎 Related results...\n')
                            for related in request.related:
                                if (cnt < search_limit):
                                    out += '\n'
                                    out += '🔗 Website: [' + related.text + '](' + related.url + ')\n'
                                    out_messages.append(out)
                                else:
                                    break
                                out = ''

                            out_messages.append('And... that\'s it! Anything else?')
                        else:
                            out_messages.append('Oops... no results.')
                        log_operation('DUCK_SEARCH', message, status=True)

                        # If we're done loading (or failing), delete the loading message.
                        try:
                            # Delete it, only if we can. It's not a bad thing though.
                            bot.delete_message(loading_message.chat.id, loading_message.message_id)
                        except:
                            pass

                    except:
                        log_operation('DUCK_SEARCH', message, status=True)
                        log_message(bot.reply_to(message, 'Sorry, something went wrong.'))

                    # Now, push the queued messages.
                    for msg in out_messages:
                        log_message(bot.send_message(message.chat.id, msg, parse_mode='Markdown'))

                    log_operation('DUCK_SEARCH_END', message, status=True)

            elif ( ( ('what' in content) or ('do' in content) ) and ('token' in content) ):
                log_operation('TOKEN_REQUEST_BEGIN', message, status=True)
                try:
                    cur = db.cursor()
                    cur.execute('SELECT COUNT(chat_id) FROM ' + mysql_table_tokens + ' WHERE chat_id = %s', (message.from_user.id,))
                    token_count = cur.fetchone()[0]

                    cur.close()

                    if (token_count > 0):
                        cur = db.cursor()
                        cur.execute('SELECT token FROM ' + mysql_table_tokens + ' WHERE chat_id = %s', (message.from_user.id,))
                        token = cur.fetchone()[0]

                        cur.close()

                        log_message(bot.reply_to(message, 'Your token is `' + token + '`.', parse_mode='Markdown'))
                    else:
                        log_message(bot.reply_to(message, 'I don\'t know who you are.'))
                except pymysql.err.Error as e:
                    log_operation('CRITICAL_ERROR', message, status=True)
                    print(e)
                    log_message(bot.reply_to(message, critical_error, parse_mode='Markdown'))
                    connect_mysql(retrying=True)
                log_operation('TOKEN_REQUEST_END', message, status=True)

            elif ( ('delete' in content) and ( ('token' in content) or ('account' in content) ) ):
                log_operation('DELETE_ACCOUNT_BEGIN', message, status=True)
                try:
                    cur = db.cursor()
                    cur.execute('SELECT COUNT(chat_id) FROM ' + mysql_table_tokens + ' WHERE chat_id = %s', (message.from_user.id,))
                    token_count = cur.fetchone()[0]

                    cur.close()

                    if (token_count > 0):
                        try:
                            cur = db.cursor()
                            cur.execute('DELETE FROM ' + mysql_table_tokens + ' WHERE chat_id = %s', (message.from_user.id,))
                            cur.close()
                            db.commit()

                            log_message(bot.reply_to(message, 'Eh... okay. :(\n\nI\'m deleting your account from my database, it makes me sad though.'))
                            log_operation(operation='DELETE_ACCOUNT', message=message, status=True)
                        except:
                            log_message(bot.reply_to(message, 'Sorry, I couldn\'t delete your account. You might want to [create an issue](' + repo_url + '/issues/new).'))
                            log_operation(operation='DELETE_ACCOUNT', message=message, status=False)
                    else:
                        log_message(bot.reply_to(message, 'I don\'t know you.'))
                        log_operation(operation='DELETE_ACCOUNT_NA', message=message, status=True)
                except pymysql.err.Error as e:
                    log_operation('CRITICAL_ERROR', message, status=True)
                    print(e)
                    log_message(bot.reply_to(message, critical_error, parse_mode='Markdown'))
                    connect_mysql(retrying=True)
                log_operation('DELETE_ACCOUNT_END', message, status=True)

            elif ('purge' in content):
                if (database_available):
                    log_operation(operation='DELETE_REQUEST_BEGIN', message=message, status=True)
                    member_type = bot.get_chat_member(message.chat.id, message.from_user.id).status
                    if ( ( (member_type == 'creator') or (member_type == 'administrator') ) or (not group_call) ):
                        # If after wiping out the request, the query is empty, report it and quit.
                        query = content.replace('purge', '', 1).replace('hey', '')[content.index('purge'):].split('purge')[0]

                        if (len(query) < 1):
                            log_message(bot.reply_to(message, "Eh... I guess you should provide an amount."))
                        else:
                            try:
                                max_delete = int(query)

                                try:
                                    # Fetch matching messages.
                                    cur = db.cursor()
                                    cur.execute('SELECT message_id FROM ' + mysql_table_log + ' WHERE chat_id = {chat_id} ORDER BY timestamp DESC LIMIT {limit}'.format(chat_id=message.chat.id, limit=max_delete))

                                    # Initialize auxiliary variables and report operation.
                                    cnt = 1
                                    row_count = str(cur.rowcount)
                                    log_operation(operation='DELETE_REQUEST(' + str(max_delete) + '/' + row_count + ')', message=message, status=True)

                                    # Delete them.

                                    for message_id in cur.fetchall():
                                        status = False
                                        try:
                                            bot.delete_message(message.chat.id, message_id)
                                            # Take them off the database.
                                            cur.execute('DELETE FROM ' + mysql_table_log + ' WHERE chat_id = {chat_id} ORDER BY timestamp DESC LIMIT {limit}'.format(chat_id=message.chat.id, limit=max_delete))
                                            status = True
                                        except:
                                            pass
                                        log_operation(operation='DELETE_MESSAGE(' + str(cnt) + '/' + row_count + ')', message_id=message_id[0], chat_id=message.chat.id, status=status)
                                        cnt += 1

                                    cur.close()
                                    db.commit()

                                except pymysql.err.Error as e:
                                    log_operation('CRITICAL_ERROR', message, status=True)
                                    print(e)
                                    log_message(bot.reply_to(message, critical_error, parse_mode='Markdown'))
                                    connect_mysql(retrying=True)
                            except ValueError:
                                log_message(bot.send_message(message.chat.id, 'That\'s not a number.'))
                    else:
                        log_message(bot.reply_to(message, 'Sorry, but you aren\'t allowed to use this module.'))

                    log_operation(operation='DELETE_REQUEST_END', message=message, status=True)
                else:
                    log_message(bot.reply_to(message, 'Sorry, but this module is disabled.'))

            # Conversational basics (because who needs AIs).
            elif ( ('no' in content) or ('thank' in content) or ('thx' in content) or ('ty' in content) or ('bye' in content) or ('cya' in content) or ('c ya' in content) or ( ('see' in content) and ('you' in content) ) ):
                log_message(bot.reply_to(message, 'Hope to see you soon!'))
            # => Greetings / welcome.
            elif ( ('hi' in content) or ('hello' in content) or ('hey' in content) ):
                log_message(bot.reply_to(message, 'Hello, is everything alright?'))
            # => Auxiliary social words and slangs.
            elif ( ('what' in content) and ('s' in content) and ('goin' in content) or ('up' in content) or ('how' in content) and ( ('do' in content) or ('in' in content) ) ):
                log_message(bot.reply_to(message, 'I\'m fine, what can I do for you, is everything alright?'))
            # => Help request: I've got a problem! (low + urgent)
            elif ( ('i' in content) and ('problem' in content) ):
                log_message(bot.reply_to(message, 'Please explain your issue and I\'ll try to help.'))
            elif ( ('what' in content) and ('s' in content) and ('name' in content) ):
                log_message(bot.reply_to(message, 'My name is ' + bot_name + '.'))
            # => Fallback: I don't know what to do!
            else:
                if (group_call):
                    log_message(bot.reply_to(message, 'I don\'t know what to do.'))
                else:
                    log_message(bot.reply_to(message, general_error, parse_mode='Markdown'))

    print('The bot is now polling...')
    bot.polling()

if __name__ == '__main__':
    main()

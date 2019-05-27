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
    print('Importing "MySQLdb"...')
    import MySQLdb
    print('Successfully imported "MySQLdb"!')
    print('Importing "MySQLError"...')
    from _mysql_exceptions import MySQLError
    print('Successfully imported "MySQLError"!')
except ImportError:
    print('Failed to import required modules, quitting...')
    exit(1)

def clear(n):
    for i in range(n):
        print('\n')

def warn_sleep():
    time.sleep(1.5);

def intro():
    clear(50)
    print('Hello! My name is ' + bot_name + ' and I\'m not very smart.')
    print('')
    print('I\'m written in Python but I don\'t rely on any AI.')
    print('Please be kind with me. :)')
    clear(5)

def main():
    github_enabled = True

    intro()
    print('Starting...')

    # Try to set up the API_KEY, if it's not present, crash.
    api_key = os.environ.get('API_KEY', '')
    if (not api_key):
        print('Missing API key, please set the environment variable API_KEY.')
        exit(1)

    mysql_hostname = os.environ.get('MYSQL_HOSTNAME', '')
    if (not mysql_hostname):
        print('Missing MySQL server hostname, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    mysql_username = os.environ.get('MYSQL_USERNAME', '')
    if (not mysql_username):
        print('Missing MySQL server username, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    if (not mysql_password):
        print('Missing MySQL server password, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    mysql_dbname = os.environ.get('MYSQL_DBNAME', '')
    if (not mysql_dbname):
        print('Missing MySQL database name, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    mysql_table = os.environ.get('MYSQL_TABLE', '')
    if (not mysql_table):
        print('Missing MySQL table name, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    try:
        # Test DB connection
        print('Connecting to the MySQL server...')
        db = MySQLdb.connect(host=mysql_hostname, user=mysql_username, passwd=mysql_password, db=mysql_dbname)
        print('Success connecting to the MySQL server!')
    except:
        print('Failed to connect to the MySQL server, all GitHub-related modules will be disabled.')
        github_enabled = False
        warn_sleep()

    try:
        # Try to create the table (if not existing).
        print('Creating table "' + mysql_table + '"...')
        cur = db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS `robbie_tokens` (chat_id int(11) NOT NULL,token varchar(40) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8')
        # Set chat_id as primary key
        cur.execute('ALTER TABLE robbie_tokens ADD PRIMARY KEY (chat_id)')
        cur.close()
        db.commit()
    except:
        pass

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

    bot = telebot.TeleBot(api_key)

    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Hey, what's up? To learn how to use me, type /help.")

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, "Using me is pretty simple, just type your query and I'll try to find it through my code!")

    @bot.message_handler(func=lambda i:True)
    def everything(message):
        content = str(message.text).lower()
        group_call = ( (message.chat.type == 'group' or message.chat.type == 'supergroup') and (bot_name.lower() in content) );
        if ( (message.chat.type == 'private') or (group_call) ):
            if ("build" in content):
                if ("twrp" in content):
                    bot.reply_to(message, "For a basic introduction, check this [XDA thread](https://forum.xda-developers.com/showthread.php?t=1943625).", parse_mode='Markdown')
                elif ("android" in content):
                    device_index = -1
                    if (len(build_guides) > 0):
                        for word in content.split():
                            try:
                                device_index = build_guides.index(word)
                                break
                            except ValueError:
                                pass
                    if (device_index > -1):
                        bot.reply_to(message, "I found a guide for your device, get it here: [Build guide for " + build_guides[device_index] + "](" +  build_guides_server + device_list_part_a + build_guides[device_index] + device_list_part_b + ").", parse_mode='Markdown')
                    else:
                        bot.reply_to(message, "A great guide to follow about this topic is the one from LineageOS, you can [check it out here](" + device_list_server + ").\n\nYou can also ask me about your specific device's build guide!", parse_mode='Markdown')
                else:
                    bot.reply_to(message, general_error, parse_mode='Markdown')

            elif ( ('my' in content) and ('github' in content) and ('username is' in content) and ('password is' in content) ):
                try:
                    cur = db.cursor()
                    cur.execute("SELECT COUNT(chat_id) FROM " + mysql_table + ' WHERE chat_id = %s', (message.from_user.id,)) # make a tuple and escape
                    token_count = cur.fetchone()[0]

                    cur.close()
                    db.commit() # try to commit (if possible)

                    if (token_count > 0):
                        bot.reply_to(message, "I know your token, please type in your search or revoke it.")
                    else:
                        if (group_call):
                            bot.reply_to(message, 'Sorry, but you\'ll need to send me a private message to use that feature, it wouldn\'t be safe here.')
                        else:
                            bot.reply_to(message, "Fine, let me see if it works...")

                            try:
                                # Parse username.
                                username = message.text[content.index("username is"):]
                                username = username.split()[2]

                                # Parse password.
                                password = message.text[content.index("pas"):]
                                password = password[password.index("is"):]
                                password = password.split()[1]
                            except:
                                pass

                            g = Github(username, password)

                            try:
                                g.get_user()
                            except:
                                bot.send_message(message.chat.id, "Sorry, those credentails aren't valid.")

                            u = g.get_user()

                            cur = db.cursor()

                            can_authorize = True

                            for auth in u.get_authorizations():
                                if (auth.note == bot_name):
                                    can_authorize = False
                                    break

                            if (can_authorize):
                                token = u.create_authorization(note=bot_name).token

                                cur.execute("INSERT INTO " + mysql_table + " (chat_id, token) VALUES (%s, %s)", (message.from_user.id, token,))
                                cur.close()
                                db.commit() # try to commit (if possible)

                                bot.send_message(message.chat.id, "Welcome " + u.name + "! Please type in your search.")
                            else:
                                bot.reply_to(message, 'Sorry, I couldn\'t get a token, please delete "' + bot_name + '" manually from your [personal access tokens](https://github.com/settings/tokens).', parse_mode='Markdown')
                except MySQLError:
                    bot.reply_to(message, critical_error, parse_mode='Markdown')
            elif ("github" in content):
                if (not github_enabled):
                    bot.reply_to(message, 'Sorry, but this module is disabled.')
                else:
                    if (" search" in content):
                        try:
                            if ("user" in content):
                                bot.reply_to(message, "Oops... that's not implemented.")
                            else:
                                # If after wiping out the request, the query is empty, report it and quit.
                                query = content.replace('github', '').replace('search', '').replace(' ', '')
                                if (len(query) < 1):
                                    bot.reply_to(message, "Eh... I guess you should search something.")
                                else:
                                    cur = db.cursor()
                                    cur.execute("SELECT (SELECT COUNT(chat_id) FROM " + mysql_table + ' WHERE chat_id = %s), (SELECT token FROM ' + mysql_table + ' WHERE chat_id = %s)', (message.from_user.id, message.from_user.id,))
                                    result = cur.fetchone()
                                    token_count = result[0]
                                    token = result[1]

                                    cur.close()

                                    if (token_count < 1):
                                        bot.reply_to(message, 'Sorry, I don\'t know you. Please tell me both your GitHub username and password.', parse_mode='Markdown')
                                    else:
                                        out_messages = []

                                        loading_message = bot.send_message(message.chat.id, 'Please wait...')
                                        bot.send_chat_action(message.chat.id, 'typing')

                                        g = Github(token)

                                        query = content.split("search")[1].replace("github", "")

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
                                                    out += repo.description + '\n'

                                                    ###############################
                                                    # TODO: Parse it as markdown  #
                                                    # prior appending.            #
                                                    ###############################

                                                    # Let's try with each known README type.
                                                    #readme = ''
                                                    #for readme_type in [ '.markdown' , '.md', '' ]:
                                                    #    try:
                                                    #        readme = str(base64.b64decode(full_repo.get_contents("README" + readme_type).content), 'utf-8')

                                                    #        # If found, stop searching.
                                                    #        break
                                                    #    except:
                                                    #        pass

                                                    # If anything is found, lets try to limit it (only if necessary).
                                                    #if (len(readme) > 0):
                                                    #    if (len(readme) > readme_char_limit):
                                                    #        readme = readme[:readme_char_limit] + '**\[...]**'

                                                    #    out += readme # (len(readme) > 0)

                                                    out_messages.append(out)
                                                    cnt += 1
                                                else:
                                                    break
                                            if (cnt < 1):
                                                out_messages.append('Oops... no results.')
                                            else:
                                                out_messages.append('And... that\'s it! Anything else?')
                                        except:
                                            out_messages.append("Failed to process query.")

                                        # If we're done loading (or failing), delete the loading message.
                                        try:
                                            # Delete it, only if we can. It's not a bad thing though.
                                            bot.delete_message(loading_message.chat.id, loading_message.message_id)
                                        except:
                                            pass

                                        # Now, push the queued messages.
                                        for msg in out_messages:
                                            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
                        except MySQLError:
                            bot.reply_to(message, critical_error, parse_mode='Markdown')
            elif ( ( ('what' in content) or ('do' in content) ) and ('token' in content) ):
                cur = db.cursor()
                cur.execute('SELECT COUNT(chat_id) FROM ' + mysql_table + ' WHERE chat_id = %s', (message.from_user.id,))
                token_count = cur.fetchone()[0]

                cur.close()

                if (token_count > 0):
                    cur = db.cursor()
                    cur.execute('SELECT token FROM ' + mysql_table + ' WHERE chat_id = %s', (message.from_user.id,))
                    token = cur.fetchone()[0]

                    cur.close()

                    bot.reply_to(message, 'Your token is `' + token + '`.', parse_mode='Markdown')
                else:
                    bot.reply_to(message, 'I don\'t know who you are.')

            elif ( ('delete' in content) and ( ('token' in content) or ('account' in content) ) ):
                try:
                    cur = db.cursor()
                    cur.execute('SELECT COUNT(chat_id) FROM ' + mysql_table + ' WHERE chat_id = %s', (message.from_user.id,))
                    token_count = cur.fetchone()[0]

                    cur.close()

                    if (token_count > 0):
                        try:
                            cur = db.cursor()
                            cur.execute('DELETE FROM ' + mysql_table + ' WHERE chat_id = %s', (message.from_user.id,))
                            cur.close()
                            db.commit()

                            bot.reply_to(message, 'Eh... okay. :(\n\nI\'m deleting your account from my database, it makes me sad though.')
                        except:
                            bot.reply_to(message, 'Sorry, I couldn\'t delete your account. You might want to [create an issue](' + repo_url + '/issues/new).')
                    else:
                        bot.reply_to(message, 'I don\'t know you.')
                except MySQLError:
                    bot.reply_to(message, critical_error, parse_mode='Markdown')

            # Conversational basics (because who needs AIs).
            elif ( ('no' in content) or ('thank' in content) or ('thx' in content) or ('ty' in content) or ('bye' in content) or ('cya' in content) or ('c ya' in content) or ( ('see' in content) and ('you' in content) ) ):
                bot.reply_to(message, 'Hope to see you soon!')
            # => Greetings / welcome.
            elif ( ('hi' in content) or ('hello' in content) or ('hey' in content) ):
                bot.reply_to(message, 'Hello, is everything alright?')
            # => Auxiliary social words and slangs.
            elif ( ('what' in content) and ('s' in content) and ('goin' in content) or ('up' in content) or ('how' in content) and ( ('do' in content) or ('in' in content) ) ):
                bot.reply_to(message, 'I\'m fine, what can I do for you, is everything alright?')
            # => Help request: I've got a problem! (low + urgent)
            elif ( ('i' in content) and ('problem' in content) ):
                bot.reply_to(message, 'Please explain your issue and I\'ll try to help.')
            elif ( ('what' in content) and ('s' in content) and ('name' in content) ):
                bot.reply_to(message, 'My name is ' + bot_name + '.')
            # => Fallback: I don't know what to do!
            else:
                bot.reply_to(message, general_error, parse_mode='Markdown')

    bot.polling()

if __name__ == '__main__':
    main()

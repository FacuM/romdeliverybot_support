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
except ImportError:
    print('Failed to import required modules, quitting...')
    exit(1)

def clear(n):
    for i in range(n):
        print('\n')

def intro():
    clear(50)
    print('Hello! My name is ' + bot_name + ' and I\'m not very smart.')
    print('')
    print('I\'m written in Python but I don\'t rely on any AI.')
    print('Please be kind with me. :)')
    clear(5)

def main():
    intro()
    print('Starting...')

    # Prepare the accounts list.
    auths = [[], [], []]

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

    bot = telebot.TeleBot(os.environ.get('API_KEY'))

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
            elif ("github" in content):
                    if ( (" username " in content) and (" is " in content) and (" password " in content) ):
                        try:
                            auths[0].index(message.chat.id)

                            bot.reply_to(message, "I know your credentails, please type in your search.")
                        except ValueError:
                            if (group_call):
                                bot.reply_to(message, 'Sorry, but you\'ll need to send me a private message to use that feature, it wouldn\'t be safe here.')
                            else:
                                # Parse username.
                                username = message.text[content.index("username"):]
                                username = username[username.index("is"):]
                                username = username.split()[1]

                                # Parse password.
                                password = message.text[content.index("pas"):]
                                password = password[password.index("is"):]
                                password = password.split()[1]

                                bot.reply_to(message, "Fine, let me see if it works...")

                                try:
                                    g = Github(username, password)
                                    bot.send_message(message.chat.id, "Welcome " + g.get_user().name + "! Please type in your search.")

                                    auths[0].append(message.chat.id)
                                    auths[1].append(username)
                                    auths[2].append(password)
                                except:
                                    bot.send_message(message.chat.id, "Sorry, those credentails aren't valid.")

                    elif (" search " in content):
                        if ("user" in content):
                            bot.reply_to(message, "Oops... that's not implemented.")
                        else:

                            # Auxiliary variables (declared to provide a proper scope).
                            username = ''
                            password = ''
                            cnt = 0

                            try:
                                index = auths[0].index(message.from_user.id)

                                username = auths[1][index]
                                password = auths[2][index]

                                loading_message = bot.send_message(message.chat.id, 'Please wait...')

                                bot.send_chat_action(message.chat.id, 'typing')

                                out_messages = []
                                try:
                                    g = Github(username, password)

                                    query = content.split("search")[1].replace("github", "")

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

                                except:
                                    out_messages.append("Sorry, those credentails aren't valid.")

                                # If we're done loading (or failing), delete the loading message.
                                try:
                                    # Delete it, only if we can. It's not a bad thing though.
                                    bot.delete_message(loading_message.chat.id, loading_message.message_id)
                                except:
                                    pass

                                # Now, push the queued messages.
                                for msg in out_messages:
                                    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

                            except ValueError:
                                bot.reply_to(message, "Sorry, I don't know you. Please tell me your username and password.")
                            #end try
                        #end if
                    else:
                        bot.reply_to(message, general_error, parse_mode='Markdown')
            # Conversational basics (because who needs AIs).
            elif ( ('no' in content) or ('thank' in content) or ('thx' in content) or ('ty' in content) or ('bye' in content) or ('cya' in content) or ('c ya' in content) or ( ('see' in content) and ('you' in content) ) ):
                index = -1
                try:
                    index = auths[0].index(message.from_user.id)
                    auths[0].remove(index)
                    auths[1].remove(index)
                    auths[2].remove(index)
                except:
                    pass
                out = 'You\'re welcome. Hope to see you soon!'
                if (index > -1):
                    out += '\n\nOh, by the way, although I just rely on a RAM-based cache which will expire on the next restart, I want to tell you that both your GitHub username and password have been taken off the database as of now.'
                bot.send_message(message.chat.id, out)
            # => Greetings / welcome.
            elif ( ('hi' in content) or ('hello' in content) or ('hey' in content) ):
                bot.send_message(message.chat.id, 'Hello, is everything alright?')
            # => Auxiliary social words and slangs.
            elif ( ('what' in content) and ('s' in content) and ('goin' in content) or ('up' in content) or ('how' in content) and ( ('do' in content) or ('in' in content) ) ):
                bot.send_message(message.chat.id, 'I\'m fine, what can I do for you, is everything alright?')
            # => Help request: I've got a problem! (low + urgent)
            elif ( ('i' in content) and ('problem' in content) ):
                bot.send_message(message.chat.id, 'Please explain your issue and I\'ll try to help.')
            # => Fallback: I don't know what to do!
            else:
                bot_message = bot.reply_to(message, general_error, parse_mode='Markdown')

    bot.polling()

if __name__ == '__main__':
    main()

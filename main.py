build_guides_server = 'https://wiki.lineageos.org'
device_list_server = build_guides_server + '/build_guides.html'
device_list_tag = 'a'
device_list_splitter = 'href="'
device_list_part_a = '/devices/'
device_list_part_b = '/build'
error = "Sorry, I couldn't find that."

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
    print('Importing "HTMLParser" from html.parser.')
    from html.parser import HTMLParser
    print('Successfully imported "HTMLParser"!')
    import requests
except ImportError:
    print('Failed to import required modules, quitting...')
    exit(1)

def main():
    print('Starting...')

    print('Parsing provided device list...') # LineageOS by default, customize.
    parser = HTMLParser()
    device_list = requests.get(device_list_server)
    build_guides = []
    if (device_list.status_code == 200):
        logging.debug('Success loading device list from server!')
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

    bot = telebot.AsyncTeleBot(os.environ.get('API_KEY'))

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
        if ("build" in content):
            if ("twrp" in content):
                bot.reply_to(message, "For a basic introduction, check this [XDA thread](https://forum.xda-developers.com/showthread.php?t=1943625).", parse_mode='Markdown')
            elif ("android" in content):
                device_index = -1
                for word in content.split():
                    try:
                        device_index = build_guides.index(word)
                        print('"' + word + '" found at index ' + str(device_index) + '!');
                        break
                    except ValueError:
                        print('"' + word + '" not in list.')
                        continue
                print(str(device_index))
                if (device_index > -1):
                    bot.reply_to(message, "I found a guide for your device, get it here: [Build guide for " + build_guides[device_index] + "](" +  build_guides_server + device_list_part_a + build_guides[device_index] + device_list_part_b + ").", parse_mode='Markdown')
                else:
                    bot.reply_to(message, "A great guide to follow about this topic is the one from LineageOS, you can [check it out here](" + device_list_server + ").\n\nYou can also ask me about your specific device's build guide!", parse_mode='Markdown')
            else:
                bot.reply_to(message, error)
        else:
            bot.reply_to(message, error)

    bot.polling()

if __name__ == '__main__':
    main()

service_name = 'Robbie'
bot_name = service_name
bot_name_lower = bot_name.lower()

import os
from dotenv import load_dotenv
import pymysql
import json

project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.bashrc'))

def create_dom(title, info, canvas_labels=None, canvas_message_count=None):
    content = '''
    <html>
     <head
      <!--Let browser know website is optimized for mobile-->
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>''' + service_name + ''' - ''' + title + '''</title>
      <!-- Compiled and minified CSS -->
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
      <!-- Icons -->
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
      <style>
        #error_text { position: relative; margin-top: 25vh; }
        @media screen and (min-width: 768px)
        {
         .brand-logo { padding-left: 1% !important; }
        }
      </style>
     </head>
     <body class="grey lighten-4">
      <header>
       <nav>
        <div class="nav-wrapper">
         <a href="#" class="brand-logo">Robbie</a>
        </div>
       </nav>
      </header>
      <main class="valign-wrapper">
       <div class="container">
       ''' + info + '''
       </div>
      </main>
      <!-- Compiled and minified JavaScript -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
      <!-- Compiled and minified ChartJS -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.js" integrity="sha256-Uv9BNBucvCPipKQ2NS9wYpJmi8DTOEfTA/nH2aoJALw=" crossorigin="anonymous"></script>
      <!-- Statistical chart -->
      <script>
        var ctx = document.getElementById('stats').getContext('2d');
        var stats = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ''' + str(canvas_labels) + ''',
                datasets: [{
                    label: 'Number of messages',
                    data: ''' + str(canvas_message_count) + ''',
                    backgroundColor: [ 'rgba(255, 99, 132, 0.2)' ],
                    borderColor: [ 'rgba(255, 99, 132, 1)' ],
                    borderWidth: 1
                }]
            }
        });
      </script>
     </body>
    </html>
    '''
    return content

def application(environ, start_response):
    if (environ.get('PATH_INFO') == '/'):
        database_available = True
        def get_environment(value):
            ret = os.environ.get(value, '')
            if (not ret):
                nonlocal database_available
                database_available = False
            return ret

        mysql_hostname = get_environment(value='MYSQL_HOSTNAME')

        mysql_username = get_environment(value='MYSQL_USERNAME')

        mysql_password = get_environment(value='MYSQL_PASSWORD')

        mysql_dbname = get_environment(value='MYSQL_DBNAME')

        mysql_table_tokens = bot_name_lower + '_tokens'

        mysql_table_log = bot_name_lower + '_log'

        '''
            Declare the DB object as global, as we're gonna write to it at least
            once.

            TODO: There must be a better solution, improve the underlying code.
        '''
        db = None
        def connect_mysql(retrying=False):

            nonlocal database_available
            try:
                nonlocal db
                # Test DB connection.
                print('Connecting to the MySQL server...')
                db = pymysql.connect(host=mysql_hostname, user=mysql_username, password=mysql_password, db=mysql_dbname)
                print('Success connecting to the MySQL server!')
            except:
                print('Failed to connect to the MySQL server, all GitHub-related modules will be disabled.')
                database_available = False
        connect_mysql()

        def log_operation():
            return

        if (database_available):
            # Fetch dates.
            cur = db.cursor()
            try:
                cur.execute('SELECT DATE_FORMAT(timestamp, "%Y-%m-%d") FROM ' + mysql_table_log + ' ORDER BY timestamp ASC')
                labels = []
                for data in cur.fetchall():
                    if not(data[0] in labels):
                        labels.append(data[0])
                cur.close()
            except pymysql.err.Error:
                database_available = False

        if (database_available):
            # Fetch messages count per day.
            message_count = []
            try:
                cur = db.cursor()
                for date in labels:
                    cur.execute('SELECT COUNT(message_id) FROM ' + mysql_table_log + ' WHERE timestamp LIKE "%' + date + '%"')
                    message_count.append(cur.fetchone()[0])
                cur.close
            except pymysql.err.Error as e:
                database_available = False

        if (database_available):
            # Fetch token count.
            token_count = -1
            try:
                cur = db.cursor()
                cur.execute('SELECT COUNT(chat_id) FROM ' + mysql_table_tokens)
                token_count = cur.fetchone()[0]
                cur.close()
            except pymysql.err.Error as e:
                database_available = False

        labels = str(json.dumps(labels))
        message_count = str(json.dumps(message_count))

        if (database_available and ((len(labels) > 0) and (len(message_count) > 0) and (token_count > -1))):
            if (token_count == 0):
                token_count = 'no'
            status = '200 OK'
            content = create_dom('Statistics', '''
             <canvas id="stats" width=1920 height=1080></canvas>
             <p>The are ''' + str(token_count) + ''' saved accounts.</p>
            ''', canvas_labels=labels, canvas_message_count=message_count)
        else:
            status = '503 INTERNAL SERVER ERROR'
            content = create_dom('Internal server error', '''
            <div id="error_text">
             <p class="center-align">
              <i class="material-icons large red-text text-lighten-2">error</i>
             </p>
             <h5 class="center-align grey-text text-darken-2">Failed to establish a reliable connection to the database server.</h5>
            </div>
            ''')
    else:
        status = '404 NOT FOUND'
        content = create_dom('Invalid request', '''
        <div id="error_text">
         <p class="center-align">
          <i class="material-icons large red-text text-lighten-2">error</i>
         </p>
         <h5 class="center-align grey-text text-darken-2">Invalid request.</h5>
        </div>
        ''')

    response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(content)))]
    start_response(status, response_headers)
    yield content.encode('utf8')

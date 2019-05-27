service_name = 'Robbie'

def create_dom(title, info):
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
        /* Force everything to fit the 95% of the viewport height. */
        html, body, main, .valign-wrapper { height: 95%; }
        #token { font-family: "Courier New", Courier, monospace; }
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
     </body>
    </html>
    '''
    return content

def application(environ, start_response):
    env = environ.copy()
    query = env['QUERY_STRING']

    if ( (environ.get('PATH_INFO') == '/') and ('code' in query) ):
        status = '200 OK'
        content = create_dom('Authorized', '''
         <h3 class="center-align grey-text text-darken-2">Thank you!</h3>
         <h5 class="center-align grey-text">Copy the following text and paste it in our chat.</h5>
         <h6 class="center-align" id="token">
          My GitHub token is ''' + query.split("code=")[1] + '''
         </h6>
        ''')
    else:
        status = '404 NOT FOUND'
        content = create_dom('Invalid request', '''
         <p class="center-align">
          <i class="material-icons large red-text text-lighten-2">error</i>
         </p>
         <h5 class="center-align grey-text text-darken-2">Invalid request.</h5>
        ''')

    response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(content)))]
    start_response(status, response_headers)
    yield content.encode('utf8')

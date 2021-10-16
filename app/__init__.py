#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE

from flask import Flask, make_response, render_template, request, send_from_directory, jsonify, url_for, redirect
from werkzeug.exceptions import HTTPException
import subprocess
import base64
import os
import tempfile
import sqlite3
import hashlib
from datetime import date, datetime
#------------------------------------------------------------------------------

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 # 50 kB
app.config['USE_DOCKER']         = True # Set to False to use a local binary.
app.config['USE_SUDO']           = True
app.config['USE_MAC']            = False
#------------------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
#------------------------------------------------------------------------------

def getDefaultStandard():
    return 'cpp17'
#------------------------------------------------------------------------------

def getCommunityEventFileName():
    return 'communityevent.txt'
#------------------------------------------------------------------------------

def getCommunityEvent():
    fName = getCommunityEventFileName()

    link = None
    title = None

    if os.path.exists(fName):
        communityEvents = open(fName, 'r').read()

        if 0 != len(communityEvents):
            link, title = communityEvents.split(';')

    return link, title
#------------------------------------------------------------------------------

def runDocker(code, insightsOptions, cppStd, versionOnly=False):
    fd, fileName = tempfile.mkstemp(suffix='.cpp')
    try:
        if not versionOnly:
            with os.fdopen(fd, 'wb') as tmp:
                # write the data into the file
                tmp.write(code.encode('utf-8'))

            # FIXME (2018-04-28): workaround as docker user cannot read file without this
            os.chmod(fileName, 436)

        fileParam = []
        if not versionOnly:
            basePath = ''

            # on mac for docker file must be under /private where we also find var
            if app.config['USE_MAC']:
                basePath = '/private'

            fileParam = [ '-v', '%s%s:/home/insights/insights.cpp' %(basePath, fileName) ]

        if app.config['USE_DOCKER']:
            # Prepend the command line with sudo
            if app.config['USE_SUDO']:
                cmd = [ 'sudo', '-u', 'pfes' ]
            else:
                cmd = []

            cmd.extend([ 'docker', 'run', '--net=none' ])
            cmd.extend(fileParam)
            cmd.extend(['--rm', '-i', 'insights-test'])
        else:
            cmd = ['insights', fileName]


        if None != insightsOptions:
            cmd.extend(insightsOptions)

        if (None != insightsOptions or None != cppStd) or versionOnly:
            cmd.append('--')

        if None != cppStd:
            cmd.append(cppStd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate(timeout=20)
        returncode     = p.returncode

    finally:
        os.remove(fileName)

    return stdout.decode('utf-8'), stderr.decode('utf-8'), returncode
#------------------------------------------------------------------------------

def buildResponse(code, stdout, stderr, insightsOptions, errCode, twcard=False, desc=''):
    if twcard:
        twdesc = code[: 100]

    if desc:
        desc = ' - ' + desc

    communitylink, communitytitle = getCommunityEvent()
    communityEventHide = ''

    if None == communitylink or None == communitytitle:
        communityEventHide = 'nocommunityevent'

    selectedInsightsOptions = getInsightsSelections(insightsOptions)
    response                = make_response(render_template('index.html', **locals()))

    return response, errCode
#------------------------------------------------------------------------------

def error_handler(errCode, code):
    stderr = 'Failed'
    stdout = '// Sorry, but your request failed due to a server error:\n// %s\n\n// Sorry for the inconvenience.\n// Please feel free to report this error.' %(errCode)

    return buildResponse('// ' + code, stdout, stderr, [] , errCode)
#------------------------------------------------------------------------------

def getSupportedOptions():
    opts = [ {'desc': 'C++ Standard'     , 'flag' : '',                         'name' : 'C++ Standard',             'selected' : False, 'label' : True,  'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'cpp98'                    , 'flag' : '-std=c++98',               'name' : 'C++ 98',                   'selected' : False, 'label' : False, 'single' : True  , 'ccopt' : True,  'cppStd' : True  },
             {'desc': 'cpp11'                    , 'flag' : '-std=c++11',               'name' : 'C++ 11',                   'selected' : False, 'label' : False, 'single' : True  , 'ccopt' : True,  'cppStd' : True  },
             {'desc': 'cpp14'                    , 'flag' : '-std=c++14',               'name' : 'C++ 14',                   'selected' : False, 'label' : False, 'single' : True  , 'ccopt' : True,  'cppStd' : True  },
             {'desc': 'cpp17'                    , 'flag' : '-std=c++17',               'name' : 'C++ 17',                   'selected' : False, 'label' : False, 'single' : True  , 'ccopt' : True,  'cppStd' : True  },
             {'desc': 'cpp2a'                    , 'flag' : '-std=c++2a',               'name' : 'C++ 2a',                   'selected' : False, 'label' : False, 'single' : True  , 'ccopt' : True,  'cppStd' : True  },
             {'desc': 'Alternative Styles'       , 'flag' : '',                         'name' : 'Alternative Styles',       'selected' : False, 'label' : True,  'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'alt-syntax-for'           , 'flag' : '-alt-syntax-for',          'name' : 'for-loops as while-loops', 'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'alt-syntax-subscription'  , 'flag' : '-alt-syntax-subscription', 'name' : 'array subscription',       'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'More Transformations'     , 'flag' : '',                         'name' : 'More Transformations',     'selected' : False, 'label' : True,  'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'all-implicit-casts'       , 'flag' : '-show-all-implicit-casts', 'name' : 'Show all implicit casts',  'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'use-libcpp'               , 'flag' : '-use-libc++',              'name' : 'Use libc++',               'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'edu-show-initlist'        , 'flag' : '-edu-show-initlist',       'name' : 'std::initializer_list',    'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
             {'desc': 'edu-show-noexcept'        , 'flag' : '-edu-show-noexcept',       'name' : 'Show noexcept internals',  'selected' : False, 'label' : False, 'single' : False , 'ccopt' : False, 'cppStd' : False },
           ]

    return opts
#------------------------------------------------------------------------------

def getInsightsSelections(selected):
    stdSelections = getSupportedOptions()
    bHaveCppStd   = False

    for opt in selected:
        for e in stdSelections:
            if opt == e['desc']:
                e['selected'] = True

                if True == e['cppStd']:
                    bHaveCppStd = True

    # check that at least one C++ standard is selected, if not insert the default.
    if not bHaveCppStd:
        for e in stdSelections:
            if e['desc'] == getDefaultStandard():
                e['selected'] = True

    return stdSelections
#------------------------------------------------------------------------------

def render(insightsOptions, code, twcard=False, desc=''):
    stdout = ''
    stderr = ''

    return buildResponse(code, stdout, stderr, insightsOptions, 200, twcard, desc)
#------------------------------------------------------------------------------

def getValidInsightsOptions(options):
    validOpts = getSupportedOptions()
    opts      = []

    for opt in options:
        for e in validOpts:
            if e['desc'] == opt:
                opts.append(e)

    return opts
#------------------------------------------------------------------------------

@app.route("/api/v1/transform", methods=['POST'])
def api():
    content = request.json
    code    = content['code']
    options = getValidInsightsOptions(content['insightsOptions'])

    insightsOptions = [opt['flag'] for opt in options if not opt['ccopt']]
    cppStd = [opt['flag'] for opt in options if opt['ccopt']]

    if 0 == len(cppStd):
        cppStd = [ getValidInsightsOptions([getDefaultStandard()])[0]['flag'] ]

    stdout, stderr, returncode = runDocker(code, insightsOptions, cppStd[0])

    if (None == stderr) or ('' == stderr):
        stderr = 'Insights exited with result code: %d' %(returncode)

    if returncode:
        stdout = 'Compilation failed!'

    resp = {}
    resp['returncode'] = returncode
    resp['stdout']     = stdout
    resp['stderr']     = stderr


    return jsonify(resp)
#------------------------------------------------------------------------------

@app.route("/api/v1/getshortlink", methods=['POST'])
def getShortLink():
    content = request.json
    code    = content['code']
    desc    = content['desc']
    rev     = content['rev']
    cppStd  = content['std']
    options = '|'.join(content['options'])
    toolId  = 1 # reserved in case we will have a windows container later.

    code = decodeCode(code)
    desc = decodeCode(desc)

    # check for missing code
    if None == code:
        resp = {}
        resp['returncode'] = 2
        resp['shortlink']  = 'No source'

        return jsonify(resp)

    # limit content length
    elif len(code) > 1000000: # 1 MB
        resp = {}
        resp['returncode'] = 1
        resp['shortlink']  = 'Source too long'

        return jsonify(resp)

    conn = sqlite3.connect(getDbName())

    c = conn.cursor()

    # Create the structure if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS shortened (id INTEGER primary key autoincrement, toolid INTEGER, code TEXT NOT NULL, desc TEXT NOT NULL, rev text NOT NULL, cppStd TEXT NOT NULL, options TEXT NOT NULL, short TEXT NOT NULL, create_at TIMESTAMP)''')

    # Check if there is already an entry for this combination
    cur = c.execute('SELECT short FROM shortened WHERE code=? AND rev=? AND cppStd=? AND options=?', (code, rev, cppStd, options,))

    rv = cur.fetchone()

    # Pack all together for the unique hash
    full = code + rev + cppStd + options
    hash_object = hashlib.sha1(full.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    surl = hex_dig[ : 8]
    retVal = 0

    if None == rv:
        now = datetime.now()
        c.execute('INSERT INTO shortened (toolid, code, desc, rev, cppStd, options, short, create_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (toolId, code, desc, rev, cppStd, options, surl, now,))
    else:
        retVal = 1
        surl = rv[0]


    # Commit and close
    conn.commit()
    conn.close()

    resp = {}
    resp['returncode'] = retVal
    resp['shortlink']  = '/s/%s' %(surl)

    return jsonify(resp)
#------------------------------------------------------------------------------

def getVersionInfo():
    stdout, stderr, returncode = runDocker('', None, None, True)

    if (None == stderr) or ('' == stderr):
        stderr = 'Insights exited with result code: %d' %(returncode)

    if returncode:
        stdout = 'Compilation failed!'

    resp = {}
    resp['returncode'] = returncode
    resp['stdout']     = stdout
    resp['stderr']     = stderr

    dockerImage = 'insights-test'
    if app.config['USE_DOCKER']:
        p = subprocess.Popen(['docker', 'images', '--filter=reference=%s' %(dockerImage), '--format', '{{.ID}} {{.CreatedAt}}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate(timeout=20)
        stdout         = stdout.decode('utf-8')
        returncode     = p.returncode
    else:
        stdout = 'Docker not used'

    resp['stdout'] += '\nDocker image "%s" info: ' %(dockerImage) + stdout + '\n'

    return resp
#------------------------------------------------------------------------------

@app.route("/api/v1/version", methods=['GET'])
def apiversion():
    resp = getVersionInfo()

    return jsonify(resp)
#------------------------------------------------------------------------------

@app.route("/version", methods=['GET'])
def version():
    resp = getVersionInfo()

    version = resp['stdout']
    version = version.replace('\n', '</br>')

    response  = make_response(render_template('version.html', **locals()))

    return response
#------------------------------------------------------------------------------

def getDbName():
    return 'urls.db'
#------------------------------------------------------------------------------

def decodeCode(code):
    try:
        # keep this in mind if, we get a incorrect length base64 string
        #code = code + '=' * (-len(code) % 4)
        # XXX: somehow we get a corrupt base64 string
        code = code.replace(' ', '+')

        # base 64 decode
        return base64.b64decode(code).decode('utf-8')

    except:
        print(repr(code))

    return None
#------------------------------------------------------------------------------

@app.route("/", methods=['GET'])
def index():
    code = ''

    return render([getDefaultStandard()], code)
#------------------------------------------------------------------------------

def proccessLink(code, desc, cppStd, insightsOptions, rev):
    if not rev or '1.0' != rev:
        return error_handler(404, 'The revision of the link is invalid.')

    return render(insightsOptions, code, twcard=True, desc=desc)
#------------------------------------------------------------------------------

@app.route("/lnk", methods=['GET', 'POST'])
def lnk():
    code    = request.args.get('code', '')
    rev     = request.args.get('rev',  '')
    cppStd  = request.args.get('std',  None)

    rawInsightsOptions = request.args.get('insightsOptions', '')
    insightsOptions    = rawInsightsOptions.split(',')

    # If this is an old link it has 'std' set. In this case use it.
    if None != cppStd:
        insightsOptions.append(cppStd)

    if code:
        code = decodeCode(code)

        if None == code:
            code = ''

    return proccessLink(code, '', cppStd, insightsOptions, rev)
#------------------------------------------------------------------------------

@app.route("/s/<link>")
def slnk(link):
    conn = sqlite3.connect(getDbName())
    c = conn.cursor()

    cur = c.execute('SELECT code, desc, rev, cppStd, options FROM shortened WHERE short = ?', (link,))

    rv = cur.fetchone()

    conn.close()

    if None == rv:
        return error_handler(404, 'There is no such link.')

    code               = rv[0]
    desc               = rv[1]
    rev                = rv[2]
    cppStd             = rv[3]
    rawInsightsOptions = rv[4]
    insightsOptions    = rawInsightsOptions.split('|')

    return proccessLink(code, desc, cppStd, insightsOptions, rev)
#------------------------------------------------------------------------------


@app.errorhandler(404)
def page_not_found(e):
#    print(request.path)
#    return redirect("/", code=302)
    return render_template('404.html'), 404
#------------------------------------------------------------------------------

@app.errorhandler(413)
def request_to_large(e):
        return error_handler(413, '')
#------------------------------------------------------------------------------

@app.errorhandler(Exception)
def other_errors(e):
    code  = request.form.get('code', '')
    ecode = 500

    print(e)

    if isinstance(e, HTTPException):
        ecode = e.code

    return error_handler(ecode, code)
#------------------------------------------------------------------------------

def getApp():
    return app
#------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(host='0.0.0.0')
#------------------------------------------------------------------------------


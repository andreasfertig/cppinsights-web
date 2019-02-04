#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE

from flask import Flask, make_response, render_template, request, send_from_directory #, redirect
from werkzeug.exceptions import HTTPException
import subprocess
import base64
import os
import tempfile
#------------------------------------------------------------------------------

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 # 50 kB
#------------------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
#------------------------------------------------------------------------------

def getDefaultStandard():
    return 'cpp17'
#------------------------------------------------------------------------------

def runDocker(code, cppStd):
    fd, fileName = tempfile.mkstemp(suffix='.cpp')
    try:
        with os.fdopen(fd, 'wb') as tmp:
            # write the data into the file
            tmp.write(code.encode('utf-8'))

        # FIXME (2018-04-28): workaround as docker user cannot read file without this
        os.chmod(fileName, 436)

        # on mac for docker file must be under /private where we also find var
        # For Mac: '/private%s:/home/insights/insights.cpp' %(fileName)
        cmd = ['sudo', '-u', 'pfes', 'docker', 'run', '--net=none', '-v', '%s:/home/insights/insights.cpp' %(fileName), '--rm', '-i', 'insights-test', cppStd]
        #cmd = [ 'docker', 'run', '--net=none', '-v', '/private%s:/home/insights/insights.cpp' %(fileName), '--rm', '-i', 'insights-test', cppStd]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate(timeout=20)
        returncode     = p.returncode

    finally:
        os.remove(fileName)

    return stdout.decode('utf-8'), stderr.decode('utf-8'), returncode
#------------------------------------------------------------------------------

def buildResponse(code, stdout, stderr, cppStdSelection, errCode):
    stdSelections = getSelections(cppStdSelection)

    response  = make_response(render_template('index.html', **locals()))

    return response, errCode
#------------------------------------------------------------------------------

def error_handler(errCode, code):
    stderr = 'Failed'
    stdout = '// Sorry, but your request failed due to a server error:\n// %s\n\n// Sorry for the inconvenience.\n// Please feel free to report this error.' %(errCode)

    return buildResponse(code, stdout, stderr, getDefaultStandard(), errCode)
#------------------------------------------------------------------------------

def getSupportedStandards():
    stds = { 'cpp98' : {'flag' : 'c++98', 'name' : 'C++ 98', 'selected' : False},
             'cpp11' : {'flag' : 'c++11', 'name' : 'C++ 11', 'selected' : False},
             'cpp14' : {'flag' : 'c++14', 'name' : 'C++ 14', 'selected' : False},
             'cpp17' : {'flag' : 'c++17', 'name' : 'C++ 17', 'selected' : False},
             'cpp2a' : {'flag' : 'c++2a', 'name' : 'C++ 2a', 'selected' : False},
           }

    return stds
#------------------------------------------------------------------------------

def mapSelectValueToOption(value):
    stdSelections = getSupportedStandards()

    std = stdSelections.get(value)
    if None != std:
        std = std['flag']
    else:
        std = getDefaultStandard()

    return '-std=%s' %(std)
#------------------------------------------------------------------------------

def getSelections(selected):
    stdSelections = getSupportedStandards()

    item = stdSelections.get(selected)
    if None != item:
        item['selected'] = True

    return stdSelections
#------------------------------------------------------------------------------

def render(cppStdSelection, code, run=False):
    if run:
        cppStd = mapSelectValueToOption(cppStdSelection)
        stdout, stderr, returncode = runDocker(code, cppStd)

        if (None == stderr) or ('' == stderr):
            stderr = 'Insights exited with result code: %d' %(returncode)

        if returncode:
            stdout = 'Compilation failed!'
    else:
        stdout = ''
        stderr = ''

    return buildResponse(code, stdout, stderr, cppStdSelection, 200)
#------------------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
def index():
    cppStd  = request.form.get('cppStd', '')
    code    = request.form.get('code',   '')
    bIsPost = ('POST' == request.method)

    return render(cppStd, code, bIsPost)
#------------------------------------------------------------------------------

@app.route("/lnk", methods=['GET', 'POST'])
def lnk():
    code    = request.args.get('code', '')
    rev     = request.args.get('rev',  '')
    cppStd  = request.args.get('std',  getDefaultStandard())

    if not rev or '1.0' != rev:
        return error_handler('The revision of the link is invalid.', '')

    if code:
        try:
            # keep this in mind if, we get a incorrect length base64 string
            #code = code + '=' * (-len(code) % 4)
            # XXX: somehow we get a corrupt base64 string
            code = code.replace(' ', '+')

            # base 64 decode
            code = base64.b64decode(code).decode('utf-8')
        except:
            print(repr(code))
            code = ''

    return render(cppStd, code, False)
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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
#------------------------------------------------------------------------------


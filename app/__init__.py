#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE

import datetime
from flask import Flask, make_response, render_template, request, send_from_directory, redirect
from werkzeug.exceptions import HTTPException
import subprocess
import base64
import os
import tempfile
#------------------------------------------------------------------------------

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024
#------------------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
#------------------------------------------------------------------------------

def runDocker(code):
    fd, fileName = tempfile.mkstemp(suffix='.cpp')
    try:
        with os.fdopen(fd, 'w') as tmp:
            # write the data into the file
            tmp.write(code)

        # FIXME (2018-04-28): workaround as docker user cannot read file without this
        os.chmod(fileName, 436)

        # on mac for docker file must be under /private where we also find var
        # For Mac: '/private%s:/home/insights/insights.cpp' %(fileName)
        #cmd = ['sudo', '-u', 'pfes', 'docker', 'run', '--net=none', '-v', '%s:/home/insights/insights.cpp' %(fileName), '--rm', '-i', 'insights-test']
        cmd = [ 'docker', 'run', '--net=none', '-v', '/private%s:/home/insights/insights.cpp' %(fileName), '--rm', '-i', 'insights-test']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate(timeout=20)
        returncode     = p.returncode

    finally:
        os.remove(fileName)

    return stdout.decode('utf-8'), stderr.decode('utf-8'), returncode
#------------------------------------------------------------------------------

def getDefaultCodeExample():
    return """#include <cstdio>
#include <vector>

int main()
{
    const char arr[10]{2,4,6,8};

    for(const char& c : arr)
    {
      printf("c=%c\\n", c);
    }
}"""
#------------------------------------------------------------------------------

def buildResponse(code, stdout, stderr, errCode):
    next_year = datetime.datetime.now() + datetime.timedelta(days=365)
    response  = make_response(render_template('index.html', **locals()))
    # store the last example in a cookie
    response.set_cookie('code', code, expires=next_year)

    return response, errCode
#------------------------------------------------------------------------------

def error_handler(errCode, code):
    stderr = 'Failed'
    stdout = '// Sorry, but your request failed due to a server error:\n// %s\n\n// Sorry for the inconvenience.\n// Please feel free to report this error.' %(errCode)

    return buildResponse(code, stdout, stderr, errCode)
#------------------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
def index():
    code = request.form.get('code', request.cookies.get('code', getDefaultCodeExample()))
    stdout, stderr, returncode = runDocker(code)

    if not stderr:
        stderr = 'Insights exited with result code: %d' %(returncode)

#        repr(stdout)

    if returncode:
        stdout = "Compilation failed!"

    return buildResponse(code, stdout, stderr, '200')
#------------------------------------------------------------------------------

@app.route("/lnk", methods=['GET', 'POST'])
def api():
    code = ''
    rev  = ''

    if 'code' in request.args:
        code = request.args['code']

    if 'rev' in request.args:
        rev  = request.args['rev']

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

    return buildResponse(code, stdout, stderr, errCode)
#------------------------------------------------------------------------------


@app.errorhandler(404)
def page_not_found(e):
#    print(request.path)
#    return redirect("/", code=302)
    return render_template('404.html'), 404
#------------------------------------------------------------------------------

@app.errorhandler(413)
def request_to_large(e):
        return error_handler('413', '')
#------------------------------------------------------------------------------

@app.errorhandler(Exception)
def other_errors(e):
    code  = request.form.get('code', request.cookies.get('code', getDefaultCodeExample()))
    ecode = 500

    if isinstance(e, HTTPException):
        ecode = e.code

    return error_handler(str(ecode), code)
#------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(host='0.0.0.0')
#------------------------------------------------------------------------------


# C++ Insights - Web Front-End

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
[![download](https://img.shields.io/badge/latest-download-blue.svg)](https://github.com/andreasfertig/cppinsights-web/releases) 
[![Build Status](https://api.travis-ci.org/andreasfertig/cppinsights-web.svg?branch=master)](https://travis-ci.org/andreasfertig/cppinsights-web) 
[![codecov](https://codecov.io/gh/andreasfertig/cppinsights-web/branch/master/graph/badge.svg)](https://codecov.io/gh/andreasfertig/cppinsights-web)
[![Try online](https://img.shields.io/badge/try-online-blue.svg)](https://cppinsights.io)



[cppinsights.io](https://cppinsights.io/) is the web front-end of C++ Insights.


```
pip3 install --user virtualenv
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt 

python3 -m pytest test.py
pytest test.py --cov=app
pytest test.py --cov=app --cov-report=html
```

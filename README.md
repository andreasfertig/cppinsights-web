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

## Short Links

There is now a short-link option. Via the usual way to obtain a link there is now a
'Request Short-Link' button. This requests a new short link from the back-end.

Short links in C++ Insights capture the currently selected options and the code entered. They do not preserve the
C++ Insights version used at the time of creation. This implies that the resulting transformation can change over time.

What a user gets back is a part of a SHA1 hash from all the captured values. This is also stored in the database and
used during lookup to prevent having the same code multiple times in the database.

For future use, the link creation time is also stored.

Please be advised to not store any confidential data in a short-link! You have no guarantees that at some point I will
not loose the database (security breach, misshapening...). 

The primary use for short-links should be easy sharing (twitter, stack overflow, etc.). There are some cases of large code samples which do not work
with long links. This is a secondary issue addressed by short-links.

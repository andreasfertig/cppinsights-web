#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE
#------------------------------------------------------------------------------

import app
#------------------------------------------------------------------------------

if __name__ == "__main__":
    a = app.getApp()
    # set the parameters for running it without sudo
    a.config['USE_DOCKER']  = True
    a.config['USE_SUDO']    = False

    # run the app
    a.run(host='0.0.0.0')
#------------------------------------------------------------------------------


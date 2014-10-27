# Test Server

This repository houses a simply Python Flask+Autobahn application which can be used to quickly test the tablet interface.

## Set up

Make sure you have the `interface` submodule cloned and then run `bower install` from within that directory. You will also need to set up a Python 2 virtual environment, activate it and then install all the dependencies.

    $ git submodule update --init
    $ cd interface && bower install && cd ..
    $ virtualenv -p /usr/bin/python2.7 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

## Running

Make sure you are in the virtual environment and it is simply a case of executing `server.py`.
 
    $ source venv/bin/activate
    $ ./server.py

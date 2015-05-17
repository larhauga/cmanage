#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Eventually a web interface
from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle

import basefunc
from lib.service import Service, Service_tree

app = Flask(__name__)
assets = Environment(app)

js = Bundle('js/main.js', filters='jsmin', output='gen/bundle.js')

@app.route('/')
def main():
    services = basefunc.session.query(Service).all()
    output = {}
    for service in services:
        output[service.name] = service.get_state()
    return render_template('plain.html', data=output)

@app.route('/relations')
def relations():
    #relations = session.query(Endpoint)
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# -*- coding:utf-8 -*-

import re
import json
from blog import *
from flask import Flask, request, make_response
from flask.ext.restful import Api, Resource, reqparse, abort

api = Api(app)


#version = __version__.strip('v')
api.add_resource(Index, '/')
api.add_resource(Help, '/api/help')

if __name__ == '__main__':
    from Tools.Config import GLOBAL
    Host = GLOBAL.get('Host')
    Port = GLOBAL.get('Port')
    Environment = GLOBAL.get('Environment')
    Debug = GLOBAL.get('Debug')

    if Environment == "dev":
        app.run(host=Host, port=int(Port), debug=Debug)
    elif Environment == "super debug":
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
        app.run(debug=Debug, host=Host, port=int(Port))

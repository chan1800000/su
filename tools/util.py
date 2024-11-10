#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os
from flask import jsonify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ResCode import ErrorCode


def make_result(data=None, code=ErrorCode.SUCCESS, msg='', other={}):
    res_info = {"status_code": -code, "status_info": msg, "info": data}
    return jsonify(dict(res_info, **other))
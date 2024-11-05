from flask_restful import Resource, reqparse
import logging
import traceback
from flask_cors import *
from tools.Pymysql_tool import *
from tools.MMMysqlDB import MyPymysqlPool
from tools.redis_utils import Redis
from tools.util import make_result
from tools.ResCode import ErrorCode
import datetime
from werkzeug.datastructures import FileStorage
from tools.set_dir import sys_param
from defined_dict import Audit_Status_ID,File_Type_ID,File_Type_Name,Del_Flag,Message_Type_ID,Message_Type_Name
from defined_dict import Msg_Status, Message_Content,List_Audit_Status_Flag,M_Quality_Organize_Id
import time
import os
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

logger = logging.getLogger('run.pm_user_api')
logger.handlers.clear()

mysql = MyPymysqlPool("cnas_db")

# 手机号校验
phone_regex = re.compile(r'1[3,4,5,6,7,8,9]\d{9}')

invalidstrList = [',', '+', ' ', '/', '?', '%', '#', '&', '=']

FILES_ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'pdf', 'JPG', 'JPEG', 'PNG', 'PDF'])



class OperateUserInfo(Resource):
    @jwt_required()   # 注释用于调试
    def get(self):
        return make_result(code=ErrorCode.ErrPARAM, msg='id error')
            
    @jwt_required()   # 注释用于调试
    def put(self):
        return make_result(code=ErrorCode.ErrPARAM, msg='id error')

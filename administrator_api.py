import sys
import re
import os
from datetime import timedelta
import datetime
import decimal
from flask_restful import Resource, reqparse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.MMMysqlDB import MyPymysqlPool
from config import settings
from tools.util import make_result
from tools.ResCode import ErrorCode
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

def decodeData(data):
    try:
        for dic in data:
            for key in dic.keys():
                # 格式化字节数据
                if isinstance(dic[key], bytes):
                    dic[key] = dic[key].decode('utf-8')

                # 格式化高精度数字
                if isinstance(dic[key], decimal.Decimal):
                    dic[key] = str(dic[key])

                # 格式化时间
                if isinstance(dic[key], datetime.datetime):
                    dic[key] = dic[key].strftime("%Y-%m-%d %H:%M:%S")

                # 格式化日期
                if isinstance(dic[key], datetime.date):
                    dic[key] = dic[key].strftime("%Y-%m-%d")
    except:
        data = None
    return data

mysql = MyPymysqlPool("su")


invalidstrList = [',', '+', ' ', '/', '?', '%', '#', '&', '=']



# 员工验证
def administrator_verify():
    current_user = get_jwt_identity()
    sql = "SELECT is_dba FROM user_info WHERE id=%s" % current_user
    db = mysql.getOne(sql)
    if db[0]['is_dba'] == 0:
        return False
    return True



# 1.1 用户注册
class UserRegistration(Resource):
    parser = reqparse.RequestParser()
    # 通用必填项，注册时间使用当前时间，当前状态默认为“待审核”
    parser.add_argument('user_name', type=str, help = 'This field cannot be blank', required=True)
    #parser.add_argument('job_number', type=str, required=True)
    parser.add_argument('phone', type=str, help = 'This field cannot be blank', required=True)
    parser.add_argument('idcard', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    parser.add_argument('password1', type=str, required=True)

    def post(self):
        data = self.parser.parse_args()
                # print(data)

        # 手机号格式错误
        if not re.match(r'^1[3-9]\d{9}$', data['phone']):
            return make_result(code=ErrorCode.ErrREQUEST, msg='手机号码格式错误!')

        # 身份证号码匹配
        pattern = r'^[1-9]\d{5}[1-2]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-2])\d{3}[0-9Xx]$'
        if not re.match(pattern, data['idcard'], flags=0):
            return make_result(code=ErrorCode.ErrREQUEST, msg='身份证号码格式错误!')

        # 密码重复验证
        if data['password'] != data['password1']:
            return make_result(code=ErrorCode.ErrREQUEST, msg='两次输入的密码不一致!')


        age = 11

        if int(data['idcard'][-2]) % 2 == 0:
            sex = "女"
        else:
            sex = "男"

        try:
            res = mysql.getAll("select audit_status,identity_card from user_info where phone='%s'" % data['phone'])
        except Exception as e:
            return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

        try:
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前时间
        except:
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 事务处理
        conn = mysql.pool.connection()
        cursor = conn.cursor()

        # 手机号已注册
        if res != -1:
            try:
                if res[0]['audit_status']==2:
                    try:
                        res11 = mysql.getAll("select id from user_info where identity_card='%s' AND phone !='%s'" % (data['idcard'], data['phone']))
                    except Exception as e:
                        return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

                    # 身份证已注册
                    if res11 != -1:
                        return make_result(code=ErrorCode.ErrPARAM, msg='该身份证已注册!')

                    up_sql = "UPDATE user_info SET `name`='%s',`password`='%s',user_name='%s',identity_card='%s'," \
                         "sex='%s',age=%s,audit_status=0 WHERE phone='%s'" % (data['user_name'],
                            data['password'], data['user_name'], data['idcard'],sex, age, data['phone'])
                    #res22 = mysql.update(up_sql)
                    cursor.execute(up_sql)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    sql_c = "SELECT id as 'user_id' FROM user_info WHERE phone='%s'" % data['phone']
                    db = mysql.getOne(sql_c)
                    return make_result(data=decodeData(db), code=ErrorCode.SUCCESS, msg='重新注册成功!')
                else:
                    return make_result(code=ErrorCode.ErrPARAM, msg='该用户已注册')
            except Exception as e:
                return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')
        else:
            try:
                res11 = mysql.getAll("select id from user_info where identity_card='%s'" % data['idcard'])
            except Exception as e:
                return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

            # 身份证已注册
            if res11 != -1:
                return make_result(code=ErrorCode.ErrPARAM, msg='该身份证已注册!')



        insertsql = "INSERT INTO user_info VALUE(0, '%s', '%s', '%s', '%s', '%s', '%s', %s, '', '%s', 0, " \
                    "(SELECT id FROM audit_status_dict WHERE name = '待审核'), (SELECT id FROM user_status_dict " \
                    "WHERE name = '使用中'))" % \
                    (data['user_name'], data['password'], data['user_name'], data['phone'], data['idcard'],
                     sex, age, create_time)


        #res1 = mysql.insert(insertsql)


        insertsql1 = "INSERT INTO user_assistant(id, user_id, employee_type, message_status) VALUE" \
                     "(0, (SELECT id FROM user_info WHERE user_name='%s' or phone='%s'), " \
                     "(SELECT id FROM employee_type_dict WHERE name='新进员工'), " \
                     "(SELECT id FROM employee_status_dict WHERE name='信息不全'))" % \
                     (data['user_name'], data['phone'])
        try:
            cursor.execute(insertsql)
            cursor.execute(insertsql1)
            conn.commit()
            cursor.close()
            conn.close()

            sql_c = "SELECT id as 'user_id' FROM user_info WHERE phone='%s'" % data['phone']
            db = mysql.getOne(sql_c)
            return make_result(data=decodeData(db),code=ErrorCode.SUCCESS, msg='注册成功!')

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return make_result(code=ErrorCode.ErrDATA, msg='数据库错误')

class Test(Resource):
    def get(self):
        sql = "SELECT * FROM user_info"
        db = mysql.getAll(sql)
        print(db)
        return make_result(data=decodeData(db), code=ErrorCode.SUCCESS, msg='注册成功!')

# 1.1 登陆
class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_name', type=str, help='This field cannot be blank', required=True)
    parser.add_argument('password', type=str, required=True)
    def post(self):
        data = self.parser.parse_args()

        sql = "SELECT a.id,a.user_name,b.role_id,c.`name` AS 'role_name' FROM user_info a " \
              "LEFT JOIN user_role_link b ON a.id=b.user_id " \
              "LEFT JOIN role c ON b.role_id=c.id " \
              "WHERE a.`disable`=0 AND a.state=0 AND a.staff=1 " \
              "AND a.user_name='%s' AND a.`password`='%s'" % (data['user_name'], data['password'])


        try:
            db = mysql.getOne(sql)
            if db == -1:
                return make_result(code=ErrorCode.ErrPARAM, msg='用户密码错误')

            access_token = create_access_token(identity=db[0]["id"], expires_delta=timedelta(seconds=3*24*60*60))

            res = {}
            res['id'] = db[0]["id"]
            res['user_name'] = db[0]["user_name"].decode('utf-8')
            res['role_id'] = db[0]["role_id"]
            res['role_name'] = db[0]["role_name"].decode('utf-8')
            res['access_token'] = str(access_token)
            return make_result(data=res, code=ErrorCode.SUCCESS, msg='登录成功')
        except:
            return make_result(code=ErrorCode.ErrDATA)


# 控制台页面接口---------


# 员工管理接口

# 1.3.1 添加员工（只有admin可以添加员工）
class AddEmployee(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_name', type=str, help='This field cannot be blank', required=True)
    parser.add_argument('phone', type=str, help='This field cannot be blank', required=True)
    parser.add_argument('password', type=str, required=True)
    parser.add_argument('password1', type=str, required=True)

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()

        current_user = get_jwt_identity()
        sql = "SELECT b.role_id FROM user_info a LEFT JOIN user_role_link b ON a.id=b.user_id " \
              "WHERE a.id=%s" % current_user
        db = mysql.getOne(sql)

        if db != -1:
            if db[0]['role_id'] != 1:
                return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')
        else:
            return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')

        # 手机号格式错误
        if not re.match(r'^1[3-9]\d{9}$', data['phone']):
            return make_result(code=ErrorCode.ErrREQUEST, msg='手机号码格式错误!')

        # 密码重复验证
        if data['password'] != data['password1']:
            return make_result(code=ErrorCode.ErrREQUEST, msg='两次输入的密码不一致!')


        try:
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前时间
        except:
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        try:
            res = mysql.getAll("select id,state from user_info where phone='%s'" % data['phone'])
        except Exception as e:
            return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

        # 手机号已注册
        if res != -1:
            return make_result(code=ErrorCode.ErrPARAM, msg='该手机号已注册!')

        try:
            res1 = mysql.getAll("select id,state from user_info where user_name='%s'" % data['user_name'])
        except Exception as e:
            return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

        # 用户名已注册
        if res1 != -1:
            return make_result(code=ErrorCode.ErrPARAM, msg='该用户名已注册!')

        # 事务处理
        conn = mysql.pool.connection()
        cursor = conn.cursor()

        insertsql = "INSERT INTO user_info VALUE(0, '%s', '%s', '%s', NULL, '%s', NULL, NULL, NULL, 0, 1, 0)" % \
                    (data['user_name'], data['password'], data['phone'], create_time)
        try:
            cursor.execute(insertsql)
            conn.commit()
            cursor.close()
            conn.close()

            return make_result(code=ErrorCode.SUCCESS, msg='添加成功!')

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return make_result(code=ErrorCode.ErrDATA, msg='数据库错误')


# 1.3.2 重命名检测
class UserCheck(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_name', type=str, required=True)

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()

        current_user = get_jwt_identity()
        sql = "SELECT b.role_id FROM user_info a LEFT JOIN user_role_link b ON a.id=b.user_id " \
              "WHERE a.id=%s" % current_user
        db = mysql.getOne(sql)
        if db != -1:
            if db[0]['role_id'] != 1:
                return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')
        else:
            return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')


        try:
            res1 = mysql.getAll("select id from user_info where user_name='%s'" % data['user_name'])
        except Exception as e:
            return make_result(code=ErrorCode.ErrDATA, msg='数据库查询错误')

        # 用户名已注册
        if res1 != -1:
            return make_result(data={"check": 0}, code=ErrorCode.SUCCESS)
        else:  # 用户可注册
            return make_result(data={"check": 1}, code=ErrorCode.SUCCESS)


# 1.3.3 员工列表
class EmployeeList(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, required=True)  # 页数
        parser.add_argument('limit', type=int, required=True)  # 每页条目数
        parser.add_argument('user_name', type=str, required=False)  # 用户名模糊搜索
        parser.add_argument('role_id', type=str, required=False)  # 队长员工下拉
        data = parser.parse_args()

        alimit = (int(data["page"]) - 1) * int(data["limit"])
        blimit = int(data["limit"])

        current_user = get_jwt_identity()
        sql = "SELECT b.role_id FROM user_info a LEFT JOIN user_role_link b ON a.id=b.user_id " \
              "WHERE a.id=%s" % current_user
        db_c = mysql.getOne(sql)

        if db_c != -1:
            if db_c[0]['role_id'] != 1:
                return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')
        else:
            return make_result(code=ErrorCode.ErrPERMIT, msg='您不是管理员!')

        sql = "SELECT a.id,a.user_name,a.notes,a.mail,a.phone,d.membership,d.income,a.add_time,e.login_time,e.ip," \
              "b.role_id,c.`name` AS 'role_name' FROM user_info a LEFT JOIN user_role_link b ON a.id=b.user_id " \
              "LEFT JOIN role c ON b.role_id=c.id LEFT JOIN employee_income d ON a.id=d.user_id " \
              "LEFT JOIN login_info e ON a.id=e.user_id WHERE a.staff=1"

        if data['user_name']:
            sql = sql + " AND a.user_name like '%" + data['user_name'] + "%'"

        if data['role_id']:
            sql = sql + " AND a.role_id=" + str(data['role_id'])

        db = mysql.getAll(sql+" GROUP BY a.id ORDER BY a.state ASC LIMIT %s,%s" % (alimit, blimit))

        # 获取条目总计
        sql_nolimit = sql + " GROUP BY a.id ORDER BY a.state ASC"
        query_count_sql = "SELECT count(1) FROM (" + sql_nolimit + ") c;"

        csql_res = decodeData(mysql.getAll(query_count_sql))

        count_dict = {}
        count_dict['count'] = csql_res[0]["count(1)"]

        return make_result(data=decodeData(db), code=ErrorCode.SUCCESS, other=count_dict)

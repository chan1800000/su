import administrator_api
from flask import Flask
from flask_restful import Api
from flask_cors import *
import administrator_api
from asgiref.wsgi import WsgiToAsgi
from flask_jwt_extended import JWTManager
wsgi_app = Flask(__name__)
CORS(wsgi_app, supports_credentials=True)

errots = {
    "ExpiredSignatureError":{
        "message":"test error handle",
        "status":401
    }
}

api = Api(wsgi_app,errors=errots)

# JWT秘钥
wsgi_app.config['JWT_SECRET_KEY'] = 'saggFGQ##434sA2g'
wsgi_app.config['JSON_SORT_KEYS'] = False
jwt = JWTManager(wsgi_app)


api.add_resource(administrator_api.UserRegistration, '/api/v1/register')  # 1.1.0 用户注册

# 1.1 登陆
api.add_resource(administrator_api.UserLogin, '/api/v1/login')

# 员工管理接口
# 1.3.1 添加员工（只有admin可以添加员工）
api.add_resource(administrator_api.AddEmployee, '/api/v1/add-employee')

# 1.3.2 重命名检测
api.add_resource(administrator_api.UserCheck, '/api/v1/user-check')

# 1.3.3 员工列表
api.add_resource(administrator_api.EmployeeList, '/api/v1/employee-list')




api.add_resource(administrator_api.Test, '/api/v1/test')

app = WsgiToAsgi(wsgi_app)

if __name__ == '__main__':
    #  True 调试模式，False 部署模式
    wsgi_app.run(host='0.0.0.0', port=8080, debug=True)

import administrator_api
from flask import Flask
from flask_restful import Api
import administrator_api
from asgiref.wsgi import WsgiToAsgi

wsgi_app = Flask(__name__)

app = Flask(__name__)
errots = {
    "ExpiredSignatureError":{
        "message":"test error handle",
        "status":401
    }
}

api = Api(wsgi_app, errors=errots)
@app.route('/')
def hello_world():
    return 'Hello World'

api.add_resource(administrator_api.UserRegistration, '/api/v1/register')  # 1.1.0 用户注册

api.add_resource(administrator_api.Test, '/api/v1/test')

app = WsgiToAsgi(wsgi_app)

if __name__ == '__main__':
    #  True 调试模式，False 部署模式
    wsgi_app.run(host='0.0.0.0', port=8080, debug=True)

import datetime
import decimal
data = [{'id': 1, 'username': b'\xe6\x9d\x8e\xe9\x9b\xb7', 'password': b'123456', 'phone': 123, 'mail': b'123@126.com', 'add_time': datetime.datetime(2024, 11, 3, 21, 43, 43), 'join_ip': b'127.0.0.1', 'notes': b'admin', 'inviter_by': None, 'disable': None, 'staff': 0, 'state': 0}]

for dic in data:
    for key in dic.keys():
        print(key)
        # 格式化字节数据
        if isinstance(dic[key], bytes):
            dic[key] = dic[key].decode('utf-8')
        print(key)
        # 格式化高精度数字
        if isinstance(dic[key], decimal.Decimal):
            dic[key] = str(dic[key])
        print("# 格式化高精度数字")
        print(key)
        # 格式化时间
        print(key)
        if isinstance(dic[key], datetime.datetime):
            dic[key] = dic[key].strftime("%Y-%m-%d %H:%M:%S")
        print("格式化时间")
        # 格式化日期
        if isinstance(dic[key], datetime.date):
            dic[key] = dic[key].strftime("%Y-%m-%d")

print(data)
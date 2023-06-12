# 在路由或其他适当的地方调用 is_token_expired() 方法并传入要检查的 token
from datetime import datetime
from jwt import jwt


def is_token_expired(token):
    try:
        decoded_token = jwt.decode(token, verify=False)  # 解码 token
        exp_timestamp = decoded_token.get('exp')  # 获取过期时间戳
        if exp_timestamp is not None:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)  # 将时间戳转换为日期时间
            if exp_datetime < datetime.now():
                return True  # token 已过期
        return False  # token 未过期
    except jwt.ExpiredSignatureError:
        return True  # token 已过期
    except jwt.InvalidTokenError:
        return True  # token 无效
def is_token_valid(token, secret_key):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])  # 使用密钥验证签名
        return True  # token 合法
    except jwt.ExpiredSignatureError:
        return False  # token 过期
    except (jwt.InvalidTokenError, jwt.DecodeError):
        return False  # token 无效

from datetime import datetime
import jwt


def is_token_valid(token, secret_key):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])  # 使用密钥验证签名
        exp_timestamp = decoded_token.get('exp')  # 获取过期时间戳
        if exp_timestamp is not None:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)  # 将时间戳转换为日期时间
            if exp_datetime < datetime.now():
                return False  # token 已过期
        return True  # token 合法
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        return False  # token 过期或无效

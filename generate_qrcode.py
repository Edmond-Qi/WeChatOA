# coding=utf-8
import time
import json
import urllib2
# 生成公众号二维码的过程:
# 1. 获取接口调用凭据: access_token
# 2. 调用生成二维码的接口，获取ticket
# 3. 使用ticket换取二维码

WECHAT_APP_ID = 'wxd1b33f201b393a4b'
WECHAT_APP_SECRET = 'ad7522c14ea5e2bfb28f3cf870e156c6'


class AccessToken(object):
    """获取接口调用凭据"""
    # 1. access_token 可能在很多地方使用，所以需要保存起来，acess_token会失效，保存有效时间，创建时间
    # 2. acess_token会失效，提供一个方法更新access_token

    _access_token = {
        'access_token': '',
        'update_time': time.time(),
        'expires_in': 7200
    }

    @classmethod
    def get_access_token(cls):
        # 如果acess为'' or 如果 access_token 已失效，重新获取
        # if access_token 为空 or access_token 已失效
        acs = cls._access_token
        if not acs.get('access_token') or (time.time() - acs.get('update_time')) > acs.get('expires_in'):
            # 获取acess_token
            # https请求方式: GET
            # https: // api.weixin.qq.com / cgi - bin / token?grant_type = client_credential
            #  & appid = APPID & secret = APPSECRET
            req_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' \
                      % (WECHAT_APP_ID, WECHAT_APP_SECRET)
            # 获取响应的内容
            res_data = urllib2.urlopen(req_url).read()
            res_dict = json.loads(res_data)

            if 'errcode' in res_dict:
                # 获取access_token失败
                raise Exception(res_dict.get('errmsg'))

            # 获取access_token成功
            # {"access_token":"ACCESS_TOKEN","expires_in":7200}
            cls._access_token['access_token'] = res_dict.get('access_token')
            cls._access_token['update_time'] = time.time()
            cls._access_token['expires_in'] = res_dict.get('expires_in')

        return cls._access_token['access_token']


from flask import Flask

# 创建Flask应用程序实例
app = Flask(__name__)


@app.route('/<int:scene_id>')
def index(scene_id):
    # http请求方式: POST
    # URL: https: // api.weixin.qq.com / cgi - bin / qrcode / create?access_token = TOKEN
    # POST数据格式：json
    # POST数据例子：{"expire_seconds": 604800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}
    req_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + AccessToken.get_access_token()
    req_dict = {
        "expire_seconds": 604800,
        "action_name": "QR_SCENE",
        "action_info": {"scene": {"scene_id": scene_id}}
    }
    # 调用生成临时二维码的接口并获取返回内容
    res_data = urllib2.urlopen(req_url, data=json.dumps(req_dict)).read()
    res_dict = json.loads(res_data)

    # 获取ticket
    ticket = res_dict.get('ticket')
    # HTTP GET请求（请使用https协议）https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=TICKET
    return '<img src="%s">' % ('https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=' + ticket)


if __name__ == '__main__':
    # 运行开发web服务器
    app.run(debug=True)

# if __name__ == '__main__':
#     print AccessToken.get_access_token()
#     print AccessToken.get_access_token()

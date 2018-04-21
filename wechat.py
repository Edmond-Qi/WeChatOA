# -*- coding:utf-8 -*-
from flask import Flask, request
from hashlib import sha1
import xmltodict
import time

# 创建Flask应用程序实例
app = Flask(__name__)

TOKEN = 'PYTHON26'

@app.route('/wechat80',methods=['POST','GET'])
def wechat():
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')

    # 1）将token、timestamp、nonce三个参数进行字典序排序
    temp = [TOKEN,timestamp,nonce]
    temp.sort()

    # 2）将三个参数字符串拼接成一个字符串进行sha1加密
    temp = ''.join(temp)
    sig = sha1(temp).hexdigest()

    # 3）开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    if signature != sig:
        return ''

    if request.method == 'GET':
        return echostr
    else:
        # 微信服务器转发粉丝发给我们公众号的信息
        # 获取发送过来的xml数据包
        req_data = request.data
        req_dict = xmltodict.parse(req_data).get('xml')

        # 当粉丝发送文本消息的时候，发什么内容，回什么内容
        msg_type = req_dict.get('MsgType')

        if 'text' == msg_type:
            res_dict = {
                'ToUserName': req_dict.get('FromUserName'),
                'FromUserName': req_dict.get('ToUserName'),
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': req_dict.get('Content')
            }
        elif 'voice' == msg_type:
            # 返回语言识别的结果 Recognition
            print req_dict.get('Recognition')
            res_dict = {
                'ToUserName': req_dict.get('FromUserName'),
                'FromUserName': req_dict.get('ToUserName'),
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': req_dict.get('Recognition')
            }
        elif 'event' == msg_type:
            # 获取事件的类型
            event = req_dict.get('Event')
            if 'subscribe' == event:
                # 关注事件
                res_dict = {
                    'ToUserName': req_dict.get('FromUserName'),
                    'FromUserName': req_dict.get('ToUserName'),
                    'CreateTime': time.time(),
                    'MsgType': 'text',
                    'Content': u'感谢关注，么么哒。'
                }

                event_key = req_dict.get('EventKey')
                print event_key
                if event_key:
                    res_dict['Content'] += u'场景值: %s' % event_key

            elif 'unsubscribe' == event:
                # 取消关注
                print '取消关注'
                res_dict = None
            else:
                # 其他事件
                print '其他事件'
                res_dict = None
        else:
            # 其他消息: 返回么么哒
            res_dict = {
                'ToUserName': req_dict.get('FromUserName'),
                'FromUserName': req_dict.get('ToUserName'),
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': u'么么哒'
            }
        if res_dict is not None:
            res_dict = {'xml': res_dict}
            # 将字典转换为xml数据包
            res_data = xmltodict.unparse(res_dict)
            return res_data
        else:
            return ''

if __name__ == '__main__':
    # 运行开发web服务器
    app.run(host='0.0.0.0',port=80,debug=True)
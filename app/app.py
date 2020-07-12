#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import redis
import requests
from enum import Enum
from bottle import route, run, default_app, request, response, post, HTTPResponse


class ProcessType(Enum):

    BLUR = 1
    GRAY = 2
    BLUR_GRAY = 3

redis_con = redis.Redis(host=os.environ['DB_PORT_6379_TCP_ADDR'], port=6379, db=0)

@route('/')
def hello():
    return 'はろー'

@route('/health')
def health():
    return 

@post('/portrait')
def portrait():
    """
    receive json from LINE webhook and transfer image url
    to the mask_rcnn server.
    json like this.
    {
        "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
        "type": "message",
        "timestamp": 1462629479859,
        "source": {
            "type": "user",
            "userId": "U4af4980629..."
        },
        "message": {
            "id": "325708",
            "type": "image",
            "contentProvider": {
            "type": "line"
            }
        }
    }
    see more https://developers.line.biz/ja/reference/messaging-api/#send-reply-message
    """
    req = request.json
    events = req['events']
    user_id = req['destination']
    print('request body without user info', events)
    try:
        process_type = _get_process_type(user_id)
    except Exception as e:
        print(e)
        return HTTPResponse(status=500)
    for event in events:
        message_type = event['message']['type']
        if message_type == 'image':
            event_message = event['message']
            image_type = event_message['contentProvider']['type']
            if image_type == 'line':
                image_url = 'https://api.line.me/v2/bot/message/{}/content'.format(event_message['id'])
            else:
                image_url = event_message['contentProvider']['originalContentUrl']
            # post image url to the mask_rcnn server
            payload = {'image_url': image_url,
                    'reply_token': event['replyToken']}
            #mask_rcnn_server sends an image to line talk room.
            headers = {'Content-Type':'application/json'}
            mask_rcnn_endpoint = 'http://{}:8080/splash/line'.format(os.getenv('GPU_PUBLIC_IP'))
            if process_type == ProcessType.BLUR:
                payload['convert_type'] = 'blur'
            elif process_type == ProcessType.GRAY:
                payload['convert_type'] = 'gray'
            else :
                payload['convert_type'] = 'blur_gray'
            print('request body to a mask_rcnn server', payload)
            res = requests.post(mask_rcnn_endpoint, data=payload, headers=headers)
            print(res)

        if message_type == 'text':
            text = event['message']['text']

            if text == 'ぼかし':
                process_type = ProcessType.BLUR
            elif text == 'グレー':
                process_type = ProcessType.GRAY
            else:
                process_type = ProcessType.BLUR_GRAY
            
            try:
                _register_process_type(user_id, process_type)
            except Exception as e:
                print(e)
                return HTTPResponse(status=500)

    return HTTPResponse(status=200)

def _get_process_type(user_id):

    process_type = redis_con.get(user_id)
    # 既にユーザ登録されていたら処理タイプを取得
    if process_type is not None:
        if int(process_type) == ProcessType.BLUR.value:
            return ProcessType.BLUR
        elif int(process_type) == ProcessType.GRAY.value:
            return ProcessType.GRAY
        else:
            return ProcessType.BLUR_GRAY

    # 初めてのユーザならDBに登録。処理はぼかし
    else:
        redis_con.set(user_id, ProcessType.BLUR.value)
        return ProcessType.BLUR

def _register_process_type(user_id, process_type):

    redis_con.set(user_id, process_type.value)
    return HTTPResponse(status=response['ResponseMetadata']['HTTPStatusCode'])

if __name__ == '__main__':
    run(host='localhost', port=8080)
else:
    # uWSGIから起動した場合
    application = default_app()

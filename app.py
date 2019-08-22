#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import route, run, default_app, request, response, post, HTTPResponse
import json
import requests
import os


@route('/')
def hello():
    return 'はろー'


@route('/health')
def health():
    return 


@post('/blur')
def blur():
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
    print('request body', request.json)
    events = request.json['events']
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
            print('request body to a mask_rcnn server', payload)
            #mask_rcnn_server sends an image to line talk room.
            headers = {'Content-Type':'application/json'}
            res = requests.post('http://{}:8080/splash/line/blur'.format(os.getenv('GPU_PUBLIC_IP')), data=payload, headers=headers)

    response = HTTPResponse(status=200)

    return response


if __name__ == '__main__':
    run(host='localhost', port=8080)
else:
    # uWSGIから起動した場合
    application = default_app()

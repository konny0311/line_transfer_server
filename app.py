#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import route, run, default_app, request, response, post, HTTPResponse
import json
import requests


@route('/health')
def hello():
    return 

@post('/gray')
def gray():
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
    message_type = request.json['message']['type']
    if message_type == 'image':
        print('image send')
        image_type = request.json['message']['contentProvider']['type']
        if image_type == 'line':
            image_url = 'https://api.line.me/v2/bot/message/{}/content'.format(request.json['message']['id'])
        else:
            image_url = request.json['message']['contentProvider']['originalContentUrl']
        # post image url to the mask_rcnn server
        payload = {'image_url': image_url
                   'reply_token': request['replyToken']}
        #mask_rcnn_server sends an image to line talk room.
        res = requests.post("http://httpbin.org/post", data=payload)
        response = HTTPResponse(status=200)
    else:
        response = HTTPResponse(status=500)

    return response


if __name__ == '__main__':
    run(host='localhost', port=8080)
else:
    # uWSGIから起動した場合
    application = default_app()

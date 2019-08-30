#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import route, run, default_app, request, response, post, HTTPResponse
import json
import requests
import os
from enum import Enum
import boto3
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('process_type')


class ProcessType(Enum):

    BLUR = 1
    GRAY = 2
    BLUR_GRAY = 3


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
    req = request.json
    print('request body', req)
    user_id = req['destination']
    process_type = _get_process_type(user_id)
    events = req['events']
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
            if process_type == ProcessType.BLUR:
                mask_rcnn_endpoint = 'http://{}:8080/splash/line/blur'.format(os.getenv('GPU_PUBLIC_IP'))
            elif process_type == ProcessType.GRAY:
                # TODO
                mask_rcnn_endpoint = 'http://{}:8080/splash/line/gray'.format(os.getenv('GPU_PUBLIC_IP'))
            else :
                # TODO
                mask_rcnn_endpoint = 'http://{}:8080/splash/line/blur_gray'.format(os.getenv('GPU_PUBLIC_IP'))

            res = requests.post(mask_rcnn_endpoint, data=payload, headers=headers)

        if message_type == 'text':
            text = event['message']['text']
            print(user_id, text)
            print(type(user_id), type(text))

            if text == 'ぼかし':
                process_type = ProcessType.BLUR
            elif text == 'グレー':
                process_type = ProcessType.GRAY
            else:
                process_type = ProcessType.BLUR_GRAY
            
            _register_process_type(user_id, process_type)


    response = HTTPResponse(status=200)

    return response


def _get_process_type(user_id):

    response = table.query(
        KeyConditionExpression=Key('UserId').eq(user_id)
    )
    # 既にユーザ登録されていたら処理タイプを取得
    if len(response['Items']) > 0:
        process_type = response['Items'][0]['Type']
        if int(process_type) == ProcessType.BLUR.value:
            return ProcessType.BLUR
        elif int(process_type) == ProcessType.GRAY.value:
            return ProcessType.GRAY
        else:
            return ProcessType.BLUR_GRAY

    # 初めてのユーザならDBに登録。処理はぼかし
    else:
        response = table.put_item(
        Item={
                'UserId': user_id,
                'Type': ProcessType.BLUR.value,
            }
        )        
        return ProcessType.BLUR

def _register_process_type(user_id, process_type):

    response = table.put_item(
    Item={
            'UserId': user_id,
            'Type': process_type.value,
        }
    )
    http_response = HTTPResponse(status=response['ResponseMetadata']['HTTPStatusCode'])

    return http_resource

if __name__ == '__main__':
    run(host='localhost', port=8080)
else:
    # uWSGIから起動した場合
    application = default_app()

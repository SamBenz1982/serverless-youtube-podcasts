import os
import time
import json
from email.utils import formatdate
from datetime import datetime

import boto3
import pafy
from jinja2 import Environment, FileSystemLoader, select_autoescape

DYNAMODB = boto3.resource('dynamodb')

METADATA_KEYS = ['id', 'description', 'duration', 'author', 'video_filesize', 'video_url',
                 'audio_filesize', 'audio_url', 'title', 'thumbnail', 'thumbnail2', 'thumbnail3', 'published',
                 'uploader', 'last_visit']


def playlist_feed(event, context):
    """Generate RSS/Podcast XML-feed for playlist"""

    playlist_id = event['pathParameters']['id']
    playlist_url = 'https://www.youtube.com/playlist?list=%s' % playlist_id

    # build URL prefix, e.g. 'https://---.execute-api.eu-west-1.amazonaws.com/dev'
    url_prefix = get_url_prefix(event)

    # extract information from YouTube video page
    try:
        playlist = pafy.get_playlist(playlist_url)

        metadata = {
            'title': '%s: %s' % (playlist['author'], playlist['title']),
            'link': playlist_url,
            'feed': '%s/playlists/%s' % (url_prefix, playlist_id),
            'generator': 'serverless-youtube-podcasts',
            'lastBuildDate': formatdate(time.time()),
            'pubDate': formatdate(time.time()),
            'category': 'TV & Film',
            'items': []
        }

        # video (mp4) vs. audio (m4a) feed?
        flavor = 'mp4'
        try:
            if 'm4a' in event['queryStringParameters']['flavor']:
                metadata['title'] += " (m4a)"
                flavor = 'm4a'
        except:
            pass

        # get list of video ids
        video_ids = map(lambda entry: entry['pafy'].videoid, list(playlist['items']))

        # identify videos, where metadata is already stored in DynamoDB
        table = DYNAMODB.Table(os.environ['VIDEOS_TABLE'])
        cached_videos = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('id').is_in(video_ids)
        )

        # iterate over items
        known_video_ids = []
        for cached_video in cached_videos['Items']:
            video_id = cached_video['id']

            # test if metadata is up-to-date
            missing_keys = [key for key in METADATA_KEYS if key not in cached_video]
            if len(missing_keys) > 0:
                trigger_update(video_id)
                continue
            known_video_ids.append(video_id)

            # parse date format '2012-10-02 17:17:24' for rfc822 conversion
            published = datetime.strptime(cached_video['published'], '%Y-%m-%d %H:%M:%S')

            # populate feed item
            item = {
                'title': cached_video['title'],
                'link': 'https://www.youtube.com/watch?v=%s' % video_id,
                'pubDate': formatdate(time.mktime(published.timetuple()), usegmt=True),
                'description': cached_video['description'],
                'thumbnail': cached_video['thumbnail'],
                'duration': cached_video['duration']
            }

            # url, type and length (size) of stream depends on format
            if flavor == 'm4a':
                item['url'] = '%s/videos/%s.m4a' % (url_prefix, video_id)
                item['type'] = 'audio/m4a'
                item['length'] = cached_video['audio_filesize']
            else:
                item['url'] = '%s/videos/%s.mp4' % (url_prefix, video_id)
                item['type'] = 'video/mp4'
                item['length'] = cached_video['video_filesize']

            # optional elements
            if 'thumbnail2' in cached_video:
                item['thumbnail2'] = cached_video['thumbnail2']
            if 'thumbnail3' in cached_video:
                item['thumbnail3'] = cached_video['thumbnail3']
            # append to items list
            metadata['items'].append(item)

        # trigger updateVideo via SNS (if necessary)
        for video_id in video_ids:
            if video_id not in known_video_ids:
                # no result? trigger updating the video via SNS
                trigger_update(video_id)

        # try to set thumbnail
        try:
            metadata['thumbnail'] = playlist['items'][0]['pafy'].thumb
        except:
            pass

        # render response
        env = Environment(loader=FileSystemLoader('.'), autoescape=select_autoescape(['xml']))
        template = env.get_template('podcast.xml')
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/rss+xml; charset=UTF-8'
            },
            'body': template.render(metadata)
        }
        return response

    except:
        response = {
            'statusCode': 404
        }
        return response


def trigger_update(video_id):
    """Trigger updating the video via SNS"""
    sns = boto3.client('sns')
    aws_account_id = os.environ['AWS_ACCOUNTID']
    message = {'video_id': video_id}
    sns.publish(
        # TODO: generate TopicArn
        TopicArn=('arn:aws:sns:eu-west-1:%s:updateVideo' % aws_account_id),
        Message=json.dumps({"default": json.dumps(message)}),
        MessageStructure='json'
    )


def get_url_prefix(event):
    """Build URL prefix, e.g. 'https://---.execute-api.eu-west-1.amazonaws.com/dev'"""
    headers = event.get('headers', dict())
    request_context = event.get('requestContext', dict())
    if 'X-Forwarded-Proto' in headers and 'Host' in headers and 'stage' in request_context:
        return headers['X-Forwarded-Proto'] + '://' + headers['Host'] + "/" + request_context['stage']

    # fallback
    return '/dummy'


def video_playback_url(event, context):
    """Generate redirect response to playback/download URL"""

    path_id = event['pathParameters']['id'].split('.')
    if len(path_id) > 1:
        video_id = path_id[0]
        video_ext = path_id[1]
    else:
        video_id = path_id[0]
        video_ext = 'mp4'

    # extract information from YouTube video page
    video = pafy.new(video_id)
    try:
        # redirect with status code 302
        if video_ext == 'm4a':
            video_stream = video.getbestaudio(preftype="m4a")
        else:
            video_stream = video.getbest(preftype="mp4")
        response = {
            'statusCode': 302,
            'headers': {
                'Location': video_stream.url
            }
        }
        return response

    except:
        response = {
            'statusCode': 404
        }
        return response


def update_video(event, context):
    """SNS handler for updating video metadata in DynamoDB"""

    # parse SNS message
    message = event['Records'][0]['Sns']['Message']
    parsed_message = json.loads(message)

    video_id = parsed_message['video_id']
    video_url = 'https://www.youtube.com/watch?v=%s' % video_id

    try:
        # retrieve video metadata
        video = pafy.new(video_url)
        best_video = video.getbest(preftype="mp4")
        best_audio = video.getbestaudio(preftype="m4a")

        # create (or overwrite) existing item in DynamoDB
        item = {
            'id': video_id,
            'description': video.description,
            'duration': video.duration,
            'author': video.author,
            'video_filesize': best_video.get_filesize(),
            'video_url': best_video.url,
            'audio_filesize': best_audio.get_filesize(),
            'audio_url': best_audio.url,
            'title': video.title,
            'thumbnail': video.thumb,
            'thumbnail2': video.bigthumb,
            'thumbnail3': video.bigthumbhd,
            'published': video.published,  # 2012-10-02 17:17:24
            'uploader': video.username,
            'last_visit': int(time.time() * 1000)
        }
        table = DYNAMODB.Table(os.environ['VIDEOS_TABLE'])
        table.put_item(Item=item)

        # return JSON for debugging purpose
        response = {
            'statusCode': 200,
            'body': json.dumps(item)
        }
        return response

    except:
        pass

    # error
    response = {
        'statusCode': 400
    }
    return response

import os
import time
import json
import boto3
import pafy

from boto3.dynamodb.conditions import Attr
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import formatdate
from youtube_dl import YoutubeDL
from youtube_dl.extractor import YoutubeIE

dynamodb = boto3.resource('dynamodb')

def playlistFeed(event, context):

    # TODO: validate playlist ID
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
            'items' : []
        }

        # get list of video ids
        video_ids = map(lambda entry: entry['pafy'].videoid, list(playlist['items']))

        # identify videos, where metadata is already stored in DynamoDB
        table = dynamodb.Table(os.environ['VIDEOS_TABLE'])
        cached_videos = table.scan(
            FilterExpression=Attr('id').is_in(video_ids)
        )

        # iterate over items
        known_video_ids = []
        for cached_video in cached_videos['Items']:
            video_id = cached_video['id']
            known_video_ids.append(video_id)

            # parse date format '2012-10-02 17:17:24' for rfc822 conversion
            pubDate = datetime.strptime(cached_video['published'], '%Y-%m-%d %H:%M:%S')

            # populate feed item
            item = {
                'title': cached_video['title'],
                'link': 'https://www.youtube.com/watch?v=%s' % video_id,
                'pubDate': formatdate(time.mktime(pubDate.timetuple()), usegmt=True),
                'description': cached_video['description'],
                'videoLength': cached_video['filesize'],
                'videoUrl': '%s/videos/%s.mp4' % (url_prefix, video_id),
                'videoType': 'video/mp4',
                'videoDuration': cached_video['duration']
            }
            metadata['items'].append(item)

        # trigger updateVideo via SNS (if necessary)
        for video_id in video_ids:
            if video_id not in known_video_ids:
                # no result? trigger updating video via SNS
                sns = boto3.client('sns')
                aws_account_id = os.environ['AWS_ACCOUNTID']
                message = { 'video_id': video_id }
                sns.publish(
                    # TODO: generate TopicArn
                    TopicArn =('arn:aws:sns:eu-west-1:%s:updateVideo' % aws_account_id),
                    Message = json.dumps({"default": json.dumps(message)}),
                    MessageStructure = 'json'
                )

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


def get_url_prefix(event):
    '''
    Build URL prefix, e.g. 'https://---.execute-api.eu-west-1.amazonaws.com/dev'
    
    :param event:  AWS Lambda event data passed to handler.
    :return: URL prefix.
    '''
    headers = event.get('headers', dict())
    request_context = event.get('requestContext', dict())
    if 'X-Forwarded-Proto' in headers and 'Host' in headers and 'stage' in request_context:
        return headers['X-Forwarded-Proto'] + '://' + headers['Host'] + "/" + request_context['stage']

    # fallback
    return '/dummy'


def videoPlaybackUrl(event, context):

    # TODO: validate video ID
    video_id = event['pathParameters']['id']
    video_url = "https://www.youtube.com/watch?v=%s" % video_id

    # extract information from YouTube video page
    dl = YoutubeDL()
    dl.params['geturl'] = True
    dl.params['dumpjson'] = True
    ie = YoutubeIE(dl)
    try:
        # redirect with status code 302
        result = ie.extract(video_url)
        response = {
            'statusCode': 302,
            'headers': {
                'Location' : result['formats'][-1]['url']
            }
        }
        return response

    except:
        response = {
            'statusCode': 404
        }
        return response


def updateVideo(event, context):

    # parse SNS message
    message = event['Records'][0]['Sns']['Message']
    parsed_message = json.loads(message)

    # TODO: validate video ID
    video_id = parsed_message['video_id']
    video_url = 'https://www.youtube.com/watch?v=%s' % video_id

    try:
        # retrieve video metadata
        video = pafy.new(video_url)
        best = video.getbest(preftype="mp4")

        # create (or overwrite) existing item in DynamoDB
        item = {
            'id': video_id,
            'description': video.description,
            'duration': video.duration,
            'author': video.author,
            'filesize': best.get_filesize(),
            'url': best.url,
            'title': video.title,
            'thumbnail': video.thumb,
            'published': video.published, # 2012-10-02 17:17:24
            'uploader': video.username,
            'last_visit': int(time.time() * 1000)
        }
        table = dynamodb.Table(os.environ['VIDEOS_TABLE'])
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
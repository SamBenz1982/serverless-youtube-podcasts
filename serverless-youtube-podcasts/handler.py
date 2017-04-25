import os
import sys
import time
import json
import boto3

# add .requirements/ to the Python search path
root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(root, '.requirements'))

from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import formatdate
from youtube_dl import YoutubeDL
from youtube_dl.extractor import YoutubePlaylistIE, YoutubeIE
from youtube_dl.utils import ExtractorError

def playlistFeed(event, context):

    # TODO: validate playlist ID
    playlist_id = event['pathParameters']['id']
    playlist_url = "https://www.youtube.com/playlist?list=%s" % playlist_id
    url_prefix = event["headers"]["X-Forwarded-Proto"] + "://" + event["headers"]["Host"] + "/" + event["requestContext"]["stage"]

    dl = YoutubeDL()
    dl.params['extract_flat'] = True
    dl.params['dumpjson'] = True
    ie = YoutubePlaylistIE(dl)

    try:
        result = ie.extract(playlist_url)
        assert result['_type'] == 'playlist'

        metadata = {
            "title": result["title"],
            "link": playlist_url,
            "feed": "%s/playlists/%s" % (url_prefix, playlist_id),
            "generator": "serverless-youtube-podcasts",
            "lastBuildDate": formatdate(time.time()),
            "pubDate": formatdate(time.time()),
            "category": "TV & Film",
            "items" : []
        }

        # additional information from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        # iterate over items
        for entry in list(result['entries']):
            video_id = entry['id']
            item = {
                "title": entry["title"],
                "link": "https://www.youtube.com/watch?v=%s" % video_id,
                "pubDate": formatdate(time.time()),
                "videoLength": "1000000",
                "videoUrl": "%s/videos/%s.mp4" % (url_prefix, video_id),
                "videoType": "video/mp4",
                "videoDuration": "01:00:00"
            }

            # add/overwrite additional information
            try:
                result = table.get_item(
                    Key={
                        'id': video_id
                    }
                )

                # convert 20161104 date format to rfc822
                pubDate = datetime.strptime(result['Item']["upload_date"], "%Y%m%d")
                item['pubDate'] = formatdate(time.mktime(pubDate.timetuple()), usegmt=True)
                # description/summary
                item['description'] = result['Item']['description']
            except:

                # no result? trigger updating video via SNS
                sns = boto3.client('sns')
                message = { 'video_id': video_id }
                response = sns.publish(
                    # TODO: generate TopicArn
                    TopicArn = 'arn:aws:sns:eu-west-1:841586162528:updateVideo',
                    Message = json.dumps({"default": json.dumps(message)}),
                    MessageStructure = 'json'
                )
                pass

            # add item to feed
            metadata["items"].append(item)

        # render response
        env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape(['xml']))
        template = env.get_template("podcast.xml")
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/rss+xml; charset=UTF-8"
            },
            "body": template.render(metadata)
        }
        return response

    except ExtractorError:
        response = {
            "statusCode": 404
        }
        return response


def videoPlaybackUrl(event, context):

    # TODO: validate video ID
    video_id = event['pathParameters']['id']
    video_url = "https://www.youtube.com/watch?v=%s" % video_id

    dl = YoutubeDL()
    dl.params['geturl'] = True
    dl.params['dumpjson'] = True
    ie = YoutubeIE(dl)

    try:
        # TODO: redirect with status code 302
        result = ie.extract(video_url)
        response = {
            "statusCode": 302,
            "headers": {
                "Location" : result['formats'][-1]['url']
            }
        }
        return response

    except ExtractorError:
        response = {
            "statusCode": 404
        }
        return response


def updateVideo(event, context):

    # parse SNS message
    message = event['Records'][0]['Sns']['Message']
    parsed_message = json.loads(message)

    # TODO: validate video ID
    video_id = parsed_message['video_id']
    video_url = "https://www.youtube.com/watch?v=%s" % video_id

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    dl = YoutubeDL()
    dl.params['geturl'] = True
    dl.params['dumpjson'] = True
    ie = YoutubeIE(dl)

    try:
        # Retrieve video metadata
        result = ie.extract(video_url)

        # Create (or overwrite) existing item in DynamoDB
        item = {
            'id': video_id,
            'age_limit': result['age_limit'],
            'description': result['description'],
            'duration': result['duration'],
            'license': result['license'],
            'title': result['title'],
            'thumbnail': result['thumbnail'],
            'upload_date': result['upload_date'], # 20161104
            'uploader': result['uploader'],
            'uploader_id': result['uploader_id'],
            'uploader_url': result['uploader_url'],
            'format': result['formats'][-1],
            'last_visit': int(time.time() * 1000)
        }
        table.put_item(Item=item)

        # Return JSON for debugging purpose
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }
        return response

    except:
        pass

    # Error?
    response = {
        "statusCode": 400
    }
    return response
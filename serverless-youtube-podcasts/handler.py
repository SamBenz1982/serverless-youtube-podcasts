import os
import sys
import time

# add .requirements/ to the Python search path
root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(root, '.requirements'))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import formatdate
from youtube_dl import YoutubeDL
from youtube_dl.extractor import YoutubePlaylistIE, YoutubeIE
from youtube_dl.utils import ExtractorError

def playlistFeed(event, context):

    # TODO: validate playlist ID
    playlist_id = event['pathParameters']['id']
    playlist_url = "https://www.youtube.com/playlist?list=%s" % playlist_id

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
            "generator": "serverless-youtube-podcasts",
            "lastBuildDate": formatdate(time.time()),
            "pubDate": formatdate(time.time()),
            "category": "TV &amp; Film",
            "items" : []
        }

        for entry in list(result['entries']):
            video_id = entry['id']
            item = {
                "title": entry["title"],
                "link": "https://www.youtube.com/watch?v=%s" % video_id,
                "pubDate": formatdate(time.time()),
                "videoLength": "0",
                "videoUrl": "/videos/%s" % video_id,
                "videoType": "video/mp4",
                "duration": "00:00:00",
                "thumbnail": "/videos/%s/thumbnail" % video_id
            }
            metadata["items"].append(item)

        # render response
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("podcast.xml")
        response = {
            "statusCode": 200,
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
            "statusCode": 200,
            "body": result['formats'][-1]['url']
        }
        return response

    except ExtractorError:
        response = {
            "statusCode": 404
        }
        return response


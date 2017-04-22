import os
import sys

# add .requirements/ to the Python search path
root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(root, '.requirements'))

from jinja2 import Environment, FileSystemLoader, select_autoescape

from youtube_dl import YoutubeDL
from youtube_dl.extractor import YoutubePlaylistIE, YoutubeIE
from youtube_dl.utils import ExtractorError

def playlistFeed(event, context):

    # TODO: validate playlist ID
    playlist_id = event['pathParameters']['id']

    dl = YoutubeDL()
    dl.params['extract_flat'] = True
    dl.params['dumpjson'] = True
    ie = YoutubePlaylistIE(dl)
    try:
        result = ie.extract("https://www.youtube.com/playlist?list=%s" % playlist_id)
        assert result['_type'] == 'playlist'
    except ExtractorError:
        return { "statusCode": 404 }

    entries = list(result['entries'])

    env = Environment(
        loader=FileSystemLoader(".") #,
        # autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("podcast.xml")

    response = {
        "statusCode": 200,
        "body": template.render(the='variables', go='here')
    }
    return response

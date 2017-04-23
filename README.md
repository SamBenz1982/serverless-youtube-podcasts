# Serverless Youtube Podcast Feeds

Access Youtube Playlists in Podcast format.

## Quick start

### Verify Python installation

Ensure Python 2.7 is available:

    python --version
    Python 2.7

Install nodeenv via `pip`:

    pip install nodeenv
    
    nodeenv --version
    1.1.2

### Install Node.js® via nodeenv

Create virtual Node.js® environment in `venv/`:

    nodeenv venv/
     * Install prebuilt node (7.9.0) ..... done.
    
Active and verify:  

    source venv/bin/activate

    node -v
    v7.9.0

    npm -v
    4.2.0

### Install Serverless Framework

npm install serverless -g # (currently 1.11)

### Deploy

Choose AWS profile:

    export AWS_PROFILE=serverless
    export AWS_REGION=eu-west-1

Deploy:

    sls deploy --region eu-west-1

    Serverless: Installing required Python packages...
    Serverless: Linking required Python packages...
    Serverless: Packaging service...
    Serverless: Unlinking required Python packages...
    Serverless: Uploading CloudFormation file to S3...
    Serverless: Uploading function .zip files to S3...
    Serverless: Uploading service .zip file to S3 (5.08 MB)...
    Serverless: Updating Stack...
    Serverless: Checking Stack update progress...
    ....................
    Serverless: Stack update finished...
    Service Information
    service: serverless-youtube-podcasts
    stage: dev
    region: eu-west-1
    api keys:
      None
    endpoints:
      GET - https://---.execute-api.eu-west-1.amazonaws.com/dev/playlists/{id}
      GET - https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/{id}
    functions:
      playlistFeed: serverless-youtube-podcasts-dev-playlistFeed
      videoPlaybackUrl: serverless-youtube-podcasts-dev-videoPlaybackUrl

Debug:

    http https://---.execute-api.eu-west-1.amazonaws.com/dev/playlists/PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA

    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Length: 11228
    Content-Type: application/json
    Date: Sat, 22 Apr 2017 19:37:18 GMT
    Via: 1.1 b24109ed1d6b9c989e349465e3747f9e.cloudfront.net (CloudFront)
    X-Amz-Cf-Id: r91d8Fm6aWwKujDltDDGwAx8RCL1Kz1mfmN9azVMyFfAQFh_eEfNJQ==
    X-Amzn-Trace-Id: sampled=0;root=1-58fbb0ee-3cd014e5f4d359cfca19856b
    X-Cache: Miss from cloudfront
    x-amzn-RequestId: 1882cbab-2793-11e7-b9e1-07e3a8ff1ed8

    <rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
    <channel>
        <title>Architecture</title>
        <description />
        <link>https://www.youtube.com/playlist?list=PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA</link>
        <generator>serverless-youtube-podcasts</generator>
        <lastBuildDate>Sat, 22 Apr 2017 19:34:01 -0000</lastBuildDate>
        <pubDate>Sat, 22 Apr 2017 19:34:01 -0000</pubDate>
        <itunes:subtitle>Architecture</itunes:subtitle>
        <itunes:summary />
        <itunes:explicit>yes</itunes:explicit>
        <itunes:category text="TV &amp; Film" />
        <itunes:image href="" />
        <media:thumbnail url="" />
        
        <item>
        <title>GOTO 2014 • Software Architecture vs. Code • Simon Brown</title>
        <description></description>
        <link>https://www.youtube.com/watch?v=GAFZcYlO5S0</link>
        <pubDate>Sat, 22 Apr 2017 19:34:01 -0000</pubDate>
        <guid isPermaLink="true">https://www.youtube.com/watch?v=GAFZcYlO5S0</guid>
        <enclosure url="/videos/GAFZcYlO5S0" length="0" type="video/mp4" />
        <media:content url="/videos/GAFZcYlO5S0" fileSize="0" type="video/mp4" />
        <itunes:subtitle>GOTO 2014 • Software Architecture vs. Code • Simon Brown</itunes:subtitle>
        <itunes:summary />
        <itunes:duration>00:00:00</itunes:duration>
        </item>
        
        <!-- ... -->
        
        <item>
        <title>GOTO 2015 • Mobile-First Architectures • Alexander Stigsen</title>
        <description></description>
        <link>https://www.youtube.com/watch?v=Xh43D4E2e2M</link>
        <pubDate>Sat, 22 Apr 2017 19:34:01 -0000</pubDate>
        <guid isPermaLink="true">https://www.youtube.com/watch?v=Xh43D4E2e2M</guid>
        <enclosure url="/videos/Xh43D4E2e2M" length="0" type="video/mp4" />
        <media:content url="/videos/Xh43D4E2e2M" fileSize="0" type="video/mp4" />
        <itunes:subtitle>GOTO 2015 • Mobile-First Architectures • Alexander Stigsen</itunes:subtitle>
        <itunes:summary />
        <itunes:duration>00:00:00</itunes:duration>
        </item>
        
    </channel>
    </rss>

### Testing locally

Install required python dependencies (populates .requirements/ directory)

    sls requirements install

    sls invoke local --function playlistFeed --path test_playlistFeed.json

    sls invoke local --function videoPlaybackUrl --path test_videoPlaybackUrl.json<?xml version="1.0" encoding="utf-8"?>

# Serverless YouTube Playlist Podcast feeds

Access YouTube playlists in Podcast format

[![Build Status](https://travis-ci.org/sedden/serverless-youtube-podcasts.svg?branch=master)](https://travis-ci.org/sedden/serverless-youtube-podcasts)
[![Dependency Status](https://gemnasium.com/badges/github.com/sedden/serverless-youtube-podcasts.svg)](https://gemnasium.com/github.com/sedden/serverless-youtube-podcasts)

## Quick start

### AWS setup

Please check the [official guide of the serverless framework](https://serverless.com/framework/docs/providers/aws/guide/credentials/#creating-aws-access-keys)
on how to setup and configure the AWS credentials for deployment.

Additionally, please create the `serverless-youtube-podcasts/serverless.env.yml` file and add your AWS account ID.

    awsAccountId: 123456789012

### Verify Python installation

Ensure Python 2.7 is available:

    python --version
    Python 2.7

Install virtualenv, if necessary:

    pip install virtualenv

### Create and activate virtual environment for Python and Node.js®

Create virtual environment in `venv/`:

    virtualenv venv/

Active:

    source venv/bin/activate

Verify:

    which python
    /Users/.../.../serverless-youtube-podcasts/venv/bin/python

#### Install Python libraries nodeenv and boto3

Install requirements defined in `requirements.txt`

    pip install -r requirements.txt

#### Install Node.Js

Install Node.Js version 6.10.2 via [nodeenv](https://github.com/ekalinin/nodeenv) into current virtualenv (-p)

    nodeenv -p -n 6.10.2
     * Install prebuilt node (6.10.2) ..... done.
     * Appending data to /Users/.../.../serverless-youtube-podcasts/venv/bin/activate
     * Overwriting /Users/.../.../serverless-youtube-podcasts/venv/bin/shim with new content

Verify Node.Js and NPM versions:

    node -v
    v6.10.2

    npm -v
    3.10.10


### Install Serverless Framework

To install the serverless framework (currently version 1.15.0)

    npm install serverless@1.15.0 -g

Change to `serverless-youtube-podcasts/` directory and install plugins:

    cd serverless-youtube-podcasts/
    npm install --save


## Deploy

Choose AWS profile:

    export AWS_PROFILE=serverless
    export AWS_REGION=eu-west-1

Deploy:

    sls deploy

    Serverless: Installing required Python packages...
    Serverless: Linking required Python packages...
    Serverless: Packaging service...
    Serverless: Unlinking required Python packages...
    Serverless: Uploading CloudFormation file to S3...
    Serverless: Uploading function .zip files to S3...
    Serverless: Uploading service .zip file to S3 (4.44 MB)...
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
      updateVideo: serverless-youtube-podcasts-dev-updateVideo

## Test

Install required python dependencies (populates `.requirements/` directory)

    sls requirements install
    
### Playlist feed

Testing the playlist feed via HTTP request:

    http https://---.execute-api.eu-west-1.amazonaws.com/dev/playlists/PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA

    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Length: 24733
    Content-Type: application/rss+xml; charset=UTF-8
    Date: Tue, 30 May 2017 22:10:16 GMT
    Via: 1.1 b24109ed1d6b9c989e349465e3747f9e.cloudfront.net (CloudFront)
    X-Amz-Cf-Id: r91d8Fm6aWwKujDltDDGwAx8RCL1Kz1mfmN9azVMyFfAQFh_eEfNJQ==
    X-Amzn-Trace-Id: sampled=0;root=1-58fbb0ee-3cd014e5f4d359cfca19856b
    X-Cache: Miss from cloudfront
    x-amzn-RequestId: 1882cbab-2793-11e7-b9e1-07e3a8ff1ed8
    
    <?xml version="1.0" encoding="utf-8"?>
    <rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
      <channel>
        <title>GOTO Conferences: Architecture</title>
        <description />
        <link>https://www.youtube.com/playlist?list=PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA</link>
        <atom:link href="https://---.execute-api.eu-west-1.amazonaws.com/dev/playlists/PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA" rel="self" type="application/rss+xml" />
        <generator>serverless-youtube-podcasts</generator>
        <lastBuildDate>Tue, 30 May 2017 22:10:16 -0000</lastBuildDate>
        <pubDate>Tue, 30 May 2017 22:10:16 -0000</pubDate>
        <itunes:subtitle>GOTO Conferences: Architecture</itunes:subtitle>
        <itunes:summary />
        <itunes:explicit>yes</itunes:explicit>
        <itunes:category text="TV &amp; Film" />

        <itunes:image href="http://i.ytimg.com/vi/GAFZcYlO5S0/default.jpg" />
        <media:thumbnail url="http://i.ytimg.com/vi/GAFZcYlO5S0/default.jpg" />

        <item>
          <title>GOTO 2014 • Software Architecture vs. Code • Simon Brown</title>
          <description>This presentation was recorded at GOTO Amsterdam 2014...</description>
          <link>https://www.youtube.com/watch?v=GAFZcYlO5S0</link>
          <pubDate>Thu, 11 Dec 2014 15:19:38 GMT</pubDate>
          <guid isPermaLink="true">https://www.youtube.com/watch?v=GAFZcYlO5S0</guid>
          <enclosure url="https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/GAFZcYlO5S0.mp4" length="360047840" type="video/mp4" />
          <media:content url="https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/GAFZcYlO5S0.mp4" fileSize="360047840" type="video/mp4" />
          <itunes:subtitle>GOTO 2014 • Software Architecture vs. Code • Simon Brown</itunes:subtitle>
          <itunes:summary />
          <itunes:duration>00:45:33</itunes:duration>
          <itunes:image href="http://i.ytimg.com/vi/GAFZcYlO5S0/default.jpg" />
        </item>
        
        <!-- ... -->
        
        <item>
          <title>GOTO 2015 • Mobile-First Architectures • Alexander Stigsen</title>
          <description>This presentation was recorded at GOTO Chicago 2015...</description>
          <link>https://www.youtube.com/watch?v=Xh43D4E2e2M</link>
          <pubDate>Tue, 14 Jul 2015 18:50:13 GMT</pubDate>
          <guid isPermaLink="true">https://www.youtube.com/watch?v=Xh43D4E2e2M</guid>
          <enclosure url="https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/Xh43D4E2e2M.mp4" length="299028788" type="video/mp4" />
          <media:content url="https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/Xh43D4E2e2M.mp4" fileSize="299028788" type="video/mp4" />
          <itunes:subtitle>GOTO 2015 • Mobile-First Architectures • Alexander Stigsen</itunes:subtitle>
          <itunes:summary />
          <itunes:duration>00:30:45</itunes:duration>
          <itunes:image href="http://i.ytimg.com/vi/Xh43D4E2e2M/default.jpg" />
        </item>
        
    </channel>
    </rss>

Testing the `playlistFeed` handler: 

    sls invoke --function playlistFeed --path test_playlistFeed.json

Testing the `playlistFeed` handler via local function invocation:

    sls invoke local --function playlistFeed --path test_playlistFeed.json


### Video playback URL

Testing the video playback URL redirection via HTTP request:

    http https://---.execute-api.eu-west-1.amazonaws.com/dev/videos/Xh43D4E2e2M
    
    HTTP/1.1 302 Found
    Connection: keep-alive
    Content-Length: 0
    Content-Type: application/json
    Date: Sun, 23 Apr 2017 22:04:40 GMT
    Location: https://r4---sn-4g5e6n7k.googlevideo.com/videoplayback?mn=sn-4g5e6n7k&mm=31&ipbits=0&key=yt6&id=o-AGPKuVqRoJBISZUwl26_
    TfPPJ59zGzg3_UdW6L5uFCpz&ip=34.253.141.39&pl=24&mime=video%2Fmp4&dur=1844.709&mv=u&source=youtube&ms=au&mt=1492984941&signature=
    C928E8ECFED9C0DAAFF8FECEFFD348C8FA3571FD.04C0D3F713BEC75552D078214F2D737899F51CEE&requiressl=yes&ratebypass=yes&sparams=dur%2Cei
    %2Cid%2Cip%2Cipbits%2Citag%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpl%2Cratebypass%2Crequiressl%2Csource%2Cupn%2Cexpire&expire=149300
    6679&upn=UpJTU8kuLfw&lmt=1471139901220366&itag=22&ei=9iT9WKL-MoO1cM70hagG
    Via: 1.1 0655b6a9cdccd22beaf4b524985b38ab.cloudfront.net (CloudFront)
    X-Amz-Cf-Id: xl59RZV4hhcgsRiouF0AToYpfw0IEWT7JlgDbta-1HY19S-awJEENA==
    X-Amzn-Trace-Id: sampled=0;root=1-58fd24f6-497e60822240fc79e2ce4746
    X-Cache: Miss from cloudfront
    x-amzn-RequestId: d83799f7-2870-11e7-bb26-7fafe85cc082

Testing the `videoPlaybackUrl` handler:

    sls invoke --function videoPlaybackUrl --path test_videoPlaybackUrl.json
    
Testing the `videoPlaybackUrl` handler via local function invocation:

    sls invoke local --function videoPlaybackUrl --path test_videoPlaybackUrl.json

### Update video request

Testing the `updateVideo` handler:

    sls invoke --function updateVideo --path test_updateVideo.json

Testing the `updateVideo` handler via local function invocation:

    sls invoke local --function updateVideo --path test_updateVideo.json
    
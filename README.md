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
    functions:
      playlistFeed: serverless-youtube-podcasts-dev-playlistFeed

$ http https://---.execute-api.eu-west-1.amazonaws.com/dev/playlists/PLEx5khR4g7PJELLTYwXZHcimWAwTUaWGA

HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 2281
Content-Type: application/json
Date: Sat, 22 Apr 2017 11:11:17 GMT
Via: 1.1 b9f07fa5534a4d783d0891d44cc959c9.cloudfront.net (CloudFront)
X-Amz-Cf-Id: EhfPoAtB8anGhC64TGfpb1Y40wWk2WWXxTI6ID4NrzK_3kdmKe7k1A==
X-Amzn-Trace-Id: sampled=0;root=1-58fb3a54-37c65b7c3575d79d02a211b7
X-Cache: Miss from cloudfront
x-amzn-RequestId: 67866ce9-274c-11e7-b8a8-f106f9ad6eea

[
    {
        "_type": "url",
        "id": "GAFZcYlO5S0",
        "ie_key": "Youtube",
        "title": "GOTO 2014 • Software Architecture vs. Code • Simon Brown",
        "url": "GAFZcYlO5S0"
    },
    {
        "_type": "url",
        "id": "Xh43D4E2e2M",
        "ie_key": "Youtube",
        "title": "GOTO 2015 • Mobile-First Architectures • Alexander Stigsen",
        "url": "Xh43D4E2e2M"
    }
]

### Testing locally

Install required python dependencies (populates .requirements/ directory)

    sls requirements install

    sls invoke local --function playlistFeed --path test_playlistFeed.json
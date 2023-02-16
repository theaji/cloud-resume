# Cloud Resume Challenge

[View resume site](https://resume.thronville.link)

## Architecture

![cloud-resume](https://user-images.githubusercontent.com/117802776/219258294-95761575-a8c5-4de5-a769-eb4a16bb3fa2.png)


## Prerequisites:

- Installed [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Ran sam init && sam deploy --guided

## Section 1: AWS Certification

I had obtained AWS SAA & SOA certifications prior to starting the challenge. Highly recommend [Adrian Cantrill](learn.cantrill.io) and [Neal Davis](https://www.udemy.com/user/63f4a578-c67a-456b-916c-ddadf73e9a26/) for exam preparation.

## Section 2-3: HTML & CSS

Used online resources to refresh knowledge of HTML and CSS basics. Ended up downloading a resume template for simplicity.

## Section 4: Static Website

Created an S3 Bucket configured for static website hosting. Added Origin Access Identity configuration to allow only CloudFront access to the S3 Bucket

```  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      WebsiteConfiguration:
        IndexDocument: 'index.html'
        
  Bucketpolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref S3Bucket
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          -
            Sid: PublicAccess
            Effect: Allow
            Principal: 
              AWS: !Sub "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${CloudFrontOriginAccessIdentity}"
            Action:
              - "s3:GetObject"
            Resource:
              - !Sub "arn:aws:s3:::${S3Bucket}/*"

  CloudFrontOriginAccessIdentity:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: CloudFront OAI for Serverless website 
```

## Section 5: HTTPS

Created a CloudFront distribution

```  
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          Compress: true
          DefaultTTL: 86400
          MinTTL: 1
          MaxTTL: 86400
          FprwardedValues:
            QueryString: false
          TargetOriginId: serverless-s3
          ViewerProtocolPolicy: 'redirect-to-https'         
        Enabled: true
        HttpVersion: 'http2'
        DefaultRootObject: 'index.html'
        IPV6Enabled: true
        Origins:
          - DomainName: !GetAtt S3Bucket.DomainName
            Id: serveless-s3
            S3OriginConfig:
              OriginAccessIdentity:
                !Join ['', ['origin-access-identity/cloudfront/', !Ref CloudFrontOriginAccessIdentity]]
        PriceClass: 'PriceClass_100'
        ViewerCertificate:
          AcmCertificateArn: !Ref Certificate 
          SslSupportMethod: sni-only
        Aliases: 
          - resume.example.com
```
 
Manually created a certificate then referenced it in the SAM template

```
  Certificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: resume.example.com 
      ValidationMethod: DNS
```


## Section 6: DNS

Added R53 record

```
  Route53Record:
    Type: AWS::Route53::RecordSetGroup
    Properties:
      HostedZoneName: <<HOSTED_ZONE_ID>>
      RecordSets:
      - Name: resume.example.com
        Type: 'A'
        AliasTarget:
          DNSName: !GetAtt 'CloudFrontDistribution.DomainName'
          EvaluateTargetHealth: false
          # The  following HosteZoneId is always used for alias records pointing to CF.
          HostedZoneId: 'Z2FDTNDATAQYW2'
```

## Section 7: Javascript

I was able to get this working after a lot of tweaking. Ran into a CORS error at this stage, but was able to resolve that by passing "Access-Control-Allow" HTTP headers.

```
<script>

fetch("https://YOURAPI.execute-api.us-east-1.amazonaws.com/Prod/put/")
fetch('https://YOURAPI.execute-api.us-east-1.amazonaws.com/Prod/get/')
    .then(response => response.json())
    .then(data => {
        document.getElementById('visitorCount').innerText = data['counter']
</script>
```

## Section 8: Database

Added below code to SAM template

```
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: cloud-resume-challenge
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: "ID"
          AttributeType: "S"
      KeySchema:
        - AttributeName: "ID"
          KeyType: "HASH"

```

## Section 9: API

The API was automatically created by SAM

## Section 10: Python

Python was used for the Lambda code. 

Return statement for Get function:

```
        return {
            "statusCode": 200,
            'headers': {
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Origin': '*'              
                        'Access-Control-Allow-Methods': 'GET'
            },
            "body": json.dumps({"counter": response['Item'].get('visitors_count'), 
            }),
        }
```

## Section 11-12: Tests & CI/CD

Used temporary credentials with Github actions to validate and build the template

```

name: validate sam and deploy
on: 
  push:
    branches: [ main ]

  
  
jobs:
  test-infra:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - uses: aws-actions/setup-sam@v1
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: $({ secrets.ACCESS_ID })
          aws-secret-access-key: $({ secrets.SECRET_ACCESS_KEY })
          aws-region: us-east-1
      - name: SAM Validate
        run: | 
          sam validate
      - name: SAM Build
        run: | 
          sam build
      - name: SAM Deploy
        run: | 
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
          
```


## Challenges & Troubleshooting

"Malformed lambda proxy response" error when calling the function from API gateway. I was able to resolve this by importing simplejson instead of json.

Test API Gateway locally:

`sam local start-api // curl http://localhost:3000/`

Test Lambda function locally:

`sam local invoke Function --event /events/event.json`

View Lambda function logs:

`sam logs -n PutFunction --stack-name cloud-resume-challege --tail`

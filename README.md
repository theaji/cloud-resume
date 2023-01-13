# Cloud Resume Challenge

[View resume site] (https://resume.thronville.link)

## Prerequisites:

- Installed [SAM CLI] (https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Ran sam init && sam deploy --guided

## Section 1: AWS Certification

I had obtained AWS SAA & SOA certifications prior to starting the challenge. Highly recommend [Adrian Cantrill] (learn.cantrill.io) and [Neal Davis] (https://www.udemy.com/user/63f4a578-c67a-456b-916c-ddadf73e9a26/) for exam preparation.

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

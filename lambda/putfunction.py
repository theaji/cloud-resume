import simplejson as json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cloud-resume-challenge')

def lambda_handler(event, context):
    response = table.get_item(
        Key={
        'ID':'0'
    })

    visitors_count = response['Item']['visitors_count']
    visitors_count = visitors_count + 1

    response = table.put_item(
        Item={
        'ID':'0',
        'visitors_count': visitors_count
    })
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, GET'
            },
        "body": json.dumps("Successfully added!"), 
            
        }

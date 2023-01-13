import simplejson as json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cloud-resume-challenge')

def lambda_handler(event, context):
    response = table.get_item(Key={
        'ID':'0'
    })
    if 'Item' in response:
        return {
            "statusCode": 200,
            'headers': {
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET'
            },
            "body": json.dumps({"counter": response['Item'].get('visitors_count'), 
            }),
        }
    else:
            print('Item ID = {} not found'.format(id)) 

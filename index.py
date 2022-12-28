import json
import textwrap

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event=None, context=None):
    aws_region = "us-west-2"

    subject = "Please verify your email address"
    sender = "noReply@prod.miffy.space"

    if event is not None:
        message = event['Records'][0]['Sns']['Message']
        message = json.loads(message)
        print(message)
        recipient = message["email"]
        token = message["token"]
    else:
        recipient = "xinyiwu2200@gmail.com"
        from uuid import uuid4
        token = uuid4()

    table = boto3.resource('dynamodb', region_name=aws_region).Table('csye6225-token')
    response = table.get_item(Key={"UserName": recipient})
    if "Item" in response.keys():
        item = response['Item']
        if item["sendStatus"] == "sent":
            return
    else:
        return

    destination = {
        'ToAddresses': [
            recipient,
        ]
    }

    link = "https://prod.miffy.space/v1/verifyUserEmail?email=%s&token=%s" % (recipient, token)
    body_text = textwrap.dedent(
        f"""
        ૮ ･ ﻌ･ა
        Welcome. 
        You are creating your account in our web.
        Please click the link below to complete validation, this link will be expired in 5 minutes.
        
        ૮ ･ ﻌ･ა
        
        {link}
        """
    )

    print(body_text)
    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=aws_region)

    try:
        response = client.send_email(
            Destination=destination,
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )

        item["sendStatus"] = "sent"
        table.put_item(Item=item)


    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        print(recipient)


if __name__ == '__main__':
    lambda_handler()

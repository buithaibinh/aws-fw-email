import json
import boto3
import base64
import os
from email import message_from_bytes
from email.policy import default


def lambda_handler(event, context):
    try:
        # Log the incoming event
        print(f"Received event: {json.dumps(event)}")

        # Parse the SNS message
        sns_message = event['Records'][0]['Sns']['Message']
        sns_data = json.loads(sns_message)

        # Decode Base64 email content
        email_content_base64 = sns_data['content']
        try:
            email_content = base64.b64decode(email_content_base64)
        except Exception as decode_error:
            print(f"Error decoding base64 content: {decode_error}")
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid base64 encoding')
            }

        # Parse the email content
        try:
            msg = message_from_bytes(email_content, policy=default)
            from_email = msg.get('From', 'Unknown Sender')
            to_email = msg.get('To', 'Unknown Recipient')
            subject = msg.get('Subject', 'No Subject')

            # Extract the body content
            body = None
            if msg.is_multipart():
                print("Email is multipart")
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                        break

            else:
                print("Email is not multipart")
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='replace')

            if body is None:
                body = "No plain text content found."

        except Exception as parse_error:
            print(f"Error parsing email: {parse_error}")
            return {
                'statusCode': 400,
                'body': json.dumps('Error parsing email content')
            }

        # Log email details for debugging
        print(f"From: {from_email}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")

        # Send the extracted content using SES
        ses_client = boto3.client('ses')
        email_to = os.environ.get('EMAIL_TO', '').split(',')
        email_from = os.environ.get('EMAIL_FROM', '')
        if not email_to or not email_from:
            print("No recipient email configured")
            return {
                'statusCode': 400,
                'body': json.dumps('No recipient email configured')
            }

        print(f"Forwarding email to: {email_to} from: {email_from}")
        # add a note to the body to indicate that it was forwarded
        body = f"{body}\n\n---\n\nThis email was forwarded by Lambda function {context.function_name}"
        response = ses_client.send_email(
            Source=email_from,
            Destination={'ToAddresses': email_to},
            Message={
                'Subject': {'Data': f"Fwd: {subject}"},
                'Body': {'Text': {'Data': f"From: {from_email}\nTo: {to_email}\n\n{body}"}}
            }
        )
        print(f"SES response: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps('Email content extracted and forwarded successfully')
        }

    except boto3.exceptions.Boto3Error as ses_error:
        print(f"SES Error: {ses_error}")
        return {
            'statusCode': 502,
            'body': json.dumps('Error sending email via SES')
        }
    except Exception as e:
        print(f"Unhandled error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error')
        }

# AWS Lambda Function

This AWS Lambda function is designed to forward emails received via SNS (Simple Notification Service) to a specified email address using SES (Simple Email Service).

## Setup

0. Configure Email receiving in SNS:
   - Create an SNS topic that will receive the email content in Base64 format.
   - Configure the email receiving rule to send the email content to the SNS topic.

1. **Environment Variables**:
   - `EMAIL_TO`: Comma-separated list of recipient email addresses.
   - `EMAIL_FROM`: The sender email address.

2. **AWS Permissions**:
   - Ensure the Lambda function has the necessary permissions to read from SNS and send emails via SES.

## Deployment

1. **Create an SNS Topic**:
   - Create an SNS topic that will receive the email content in Base64 format.

2. **Create a Lambda Function**:
   - Deploy the provided `lambda_function.py` as a Lambda function.
   - Set the necessary environment variables (`EMAIL_TO` and `EMAIL_FROM`).

3. **Subscribe Lambda to SNS Topic**:
   - Subscribe the Lambda function to the SNS topic created in step 1.

## Usage

When an email is received by the SNS topic, the Lambda function will:
1. Decode the Base64 email content.
2. Parse the email to extract the sender, recipient, subject, and body.
3. Forward the email content to the specified recipient(s) using SES.

## Error Handling

The Lambda function handles the following errors:
- Invalid Base64 encoding.
- Errors in parsing the email content.
- Errors in sending the email via SES.

## Example Event

Here is an example of the SNS event that the Lambda function expects:

```json
{
  "Records": [
    {
      "Sns": {
        "Message": "{\"content\": \"<Base64 encoded email content>\"}"
      }
    }
  ]
}
```

## License

This project is licensed under the MIT License.

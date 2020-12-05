# AWS Serverless POC for Authy API (by Twilio)

This is a proof of concept (POC) project and also a starting point for cloud native application to implement two-factor-authentication (2FA) and passwordless login, taking advantage of Authy API. We know that serverless applications are highly cost effective and deliver optimal throughput for applications with auto-scale based on service demand and provision high availability for continuous up time.

This project also uses Infrastructure-as-Code (IaC), more specifically AWS CloudFormation to build up the initial tech stack with AWS IAM, API Gateway and Lambda Functions (Function as a Service - FaaS). AWS stack uses Free Tier account type and Twilio Trial accounts for this implementation.

At this point, the POC only implements "Create an Authy User" Authy API request as an example and works as a starting point to handle enhanced authentication processes.

## Project Steps

- [x] Configure AWS free tier account;
- [x] Download AWS client (CLI) and setup your local environment;
- [x] Bring up the the stack with AWS CloudFormation for the serverless stack:
	- [x] AWS API Gateway [resource + endpoints]
	- [x] AWS Lambda Functions [python3] & IAM role for execution grant;
- [x] Setup Twilio Authy account;
- [x] Build and upload python lambda function;
	- [x] Test lambda function response;
- [x] Deploy API endpoints to public access;
	- [x] Test API request and response;
- [ ] NEXT: Build up an application & implement other Authy integrations.
- [ ] NEXT: Automate with a source control system and deployment pipeline.

## AWS Free Tier Account

AWS free account creation is pretty straight forward and can be achieved by following the steps in [AWS website](https://aws.amazon.com/free).

Once the account is created, login to [AWS console](https://console.aws.amazon.com) and generate and capture an access key and secret under the section *Your Security Credentials*.

> NOTE : Best practices say that a new IAM with less privilege must be created to access your account, but for this POC we are skipping this step.

## Install AWS CLI

Go to [AWS CLI webpage](https://aws.amazon.com/cli/), download and install the client.

To be able to access AWS accounts through CLI, access key, secret and default region must be available under home .aws directory.

Example:

```sh
$ aws configure
```
```txt
AWS Access Key ID [None]: AKIAZ3NGDFHGHJH2O5VX
AWS Secret Access Key [None]: 34qySGB5U8SHi42gh1xghddfjsNkS/Vg5T8RweK4dgG
Default region name [None]: us-east-1
Default output format [None]: yaml
```

```sh
$ cat ~/.aws/credentials
```
```txt
[default]
aws_access_key_id = AKIAZ3NGDFHGHJH2O5VX
aws_secret_access_key = 34qySGB5U8SHi42gh1xghddfjsNkS/Vg5T8RweK4dgG
region = us-east-1
output=yaml
```

Testing the CLI:

```sh
$ aws iam get-user
```
```yaml
User:
  Arn: arn:aws:iam::767955521446:root
  CreateDate: '2020-12-03T23:22:03+00:00'
  PasswordLastUsed: '2020-12-04T08:52:27+00:00'
  UserId: '767955521446'
```

Now we are ready to deploy our infrastructure with AWS CloudFormation.

## Building up initial infrastructure with AWS CloudFormation

Now, let's use the AWS CLI command line to import the basic cloud infrastructure that will call Authy authentication API.

First, get [cloudformation-authy-basic-stack.yaml](./resources/cloudformation-authy-basic-stack.yaml) code and run the following command to create the basic stack:

```sh
$ aws cloudformation create-stack --stack-name authy-app-stack --template-body file://./cloudformation-authy-basic-stack.yaml --capabilities CAPABILITY_NAMED_IAM
```

As response we get the Amazon Resource Name (ARN) for the stack:

```txt
StackId: arn:aws:cloudformation:us-east-1:767916421446:stack/authy-app-stack/4acbb5f0-3675-11eb-90dc-129177fe7919
```

We can go to [AWS Console > CLoudFormation](https://console.aws.amazon.com/cloudformation) to check the status...

![AWS CloufFormation Console](./images/img01.png)

... or evaluate through the CLI ...

```sh
$ aws cloudformation describe-stacks --stack-name authy-app-stack
```
```yaml
Stacks:
- Capabilities:
  - CAPABILITY_NAMED_IAM
  CreationTime: '2020-12-04T21:20:09.560000+00:00'
  DisableRollback: false
  DriftInformation:
    StackDriftStatus: NOT_CHECKED
  EnableTerminationProtection: false
  NotificationARNs: []
  RollbackConfiguration: {}
  StackId: arn:aws:cloudformation:us-east-1:767916421446:stack/authy-app-stack/4acbb5f0-3675-11eb-90dc-129177fe7919
  StackName: authy-app-stack
  StackStatus: CREATE_COMPLETE
  Tags: []
```

All good. At this point we have AWS stack up and running with the following components:

- IAM Role to execute Lambda function
- Lambda Function with basic instructions
- API Gateway with single resource and method (plus CORS - OPTION method)

> NOTE #1: To extract the code to build up the infrastructure the tool [Former2](https://former2.com) was used.

> NOTE #2: Alternatively this can also be done with [Terraform by HashiCorp](https://www.terraform.io/). Let's stick to AWS own infrastructure for this POC.

Next, let's create a Twilio account and build the Lambda function and deploy it to AWS.

## Setup Twilio Authy Account

In order to get usage of the authentication API, get a free trial account from [twilio.com/try-twilio](https://www.twilio.com/try-twilio).

After following the steps create an [Authy Application](https://www.twilio.com/console/authy/applications/).

It's important to remember to capture Authy Production API Key of your application:

![Authy Production API Key](./images/img02.png)

> NOTE : More information can be found at [twilio.com/docs/authy/api](https://www.twilio.com/docs/authy/api)

## Build and Upload Python Lambda Function

Now, let's create some Python code, test it locally and upload it as a lambda function to be used by our API.

> NOTE : this step assumes that you already have Python 3.8.x properly setup.

First, setup environment variable with Authy Production API Key, as follows:

```sh
$ echo "export TWILIO_AUTHY_API_KEY='R24pSHJd8eXgqA9XX1zzSV17ytGYw2A3'" > .env
$ source .env
```

> NOTE: It's a best practice to "hide" the key as an environment variable and not pass it in clear text to the application.

Create a directory to store the code and download all package dependencies locally as you need to push it to the cloud the whole code.

```sh
$ mkdir -p source/package
$ cd source/
$ pip3 install --target package authy
```

```txt
Collecting authy
  Using cached authy-2.2.6.tar.gz (11 kB)
Collecting requests>=2.2.1
  Using cached requests-2.25.0-py2.py3-none-any.whl (61 kB)
Collecting six>=1.8.0
  Using cached six-1.15.0-py2.py3-none-any.whl (10 kB)
Collecting chardet<4,>=3.0.2
  Using cached chardet-3.0.4-py2.py3-none-any.whl (133 kB)
Collecting certifi>=2017.4.17
  Using cached certifi-2020.11.8-py2.py3-none-any.whl (155 kB)
Collecting idna<3,>=2.5
  Using cached idna-2.10-py2.py3-none-any.whl (58 kB)
Collecting urllib3<1.27,>=1.21.1
  Using cached urllib3-1.26.2-py2.py3-none-any.whl (136 kB)
Using legacy setup.py install for authy, since package 'wheel' is not installed.
Installing collected packages: chardet, certifi, idna, urllib3, requests, six, authy
    Running setup.py install for authy ... done
Successfully installed authy-2.2.6 certifi-2020.11.8 chardet-3.0.4 idna-2.10
    requests-2.25.0 six-1.15.0 urllib3-1.26.2
```

Now let's create the Python code ```index.py``` to call [Authy API to Create and Authy User](https://www.twilio.com/docs/authy/api).

```sh
$ vi index.py
```

```py
import os
from authy.api import AuthyApiClient

def lambda_handler(event, context):
    api_key = os.getenv('TWILIO_AUTHY_API_KEY')
    authy_api = AuthyApiClient(api_key)
    p_email = event.get('email')
    p_phone = event.get('phone')
    p_ccode = event.get('ccode')
    user = authy_api.users.create(email=p_email,phone=p_phone,country_code=p_ccode)
    if user.ok():
        user_id = user.id
        return {"message":"User created successfully.","user":{"id":user_id},"success":"true"}
    else:
        return user.errors()

if __name__ == '__main__':
    import pprint
    import sys

    response = lambda_handler({'email': sys.argv[1],'phone': sys.argv[2],'ccode': sys.argv[3]}, None)
    pprint.pprint(response)
```

Now let's test the API call to register an authy user, passing arguments: e-mail, phone (with area code), country code.

```sh
$ PYTHONPATH=package python3 index.py xyz@gmail.com 51996770547 55
```

Successful response:

```json
{
	"message": "User created successfully.",
 	"success": "true",
 	"user": {
 		  "id": 314250130
 		}
}
```

Try with some bad data to validade:

```sh
$ PYTHONPATH=package python3 index.py bademail 51996770547 55
```

Error response:

```json
{
	"email": "is invalid",
	"message": "User was not valid"
}
```

Let's package the function code in a format that AWS lambda will understand.

```sh
$ cd package/
$ zip -r ../index.zip .
$ cd ..
$ zip index.zip index.py
```

Done. Let's upload the code on top of our existing lambda function created from CloudFormation stack.

```sh
$ aws lambda update-function-code --function-name authy-create-user \
                                  --zip-file fileb://./index.zip
```
```yaml
CodeSha256: Zu7ZnmsZs8y3R+xxzErvTzwlt6gS2dr5j4KunIkMSt4=
CodeSize: 1007722
Description: ''
Environment:
  Variables:
    TWILIO_AUTHY_API_KEY: authy-app-production-api-key
FunctionArn: arn:aws:lambda:us-east-1:767916421446:function:authy-create-user
FunctionName: authy-create-user
Handler: index.lambda_handler
LastModified: 2020-12-04T22:56:13.705+0000
LastUpdateStatus: Successful
MemorySize: 128
RevisionId: d06fd218-5ffb-4f09-8452-da222ea09a90
Role: arn:aws:iam::767916421446:role/lambda-access
Runtime: python3.8
State: Active
Timeout: 3
TracingConfig:
  Mode: PassThrough
Version: $LATEST
```

Success! Let's update the environment variable into the AWS lambda environment variable too.

```sh
$ aws lambda update-function-configuration --function-name authy-create-user \
                                           --environment Variables="{TWILIO_AUTHY_API_KEY=$TWILIO_AUTHY_API_KEY}"
```
```yaml
CodeSha256: Zu7ZnmsZs8y3R+xxzErvTzwlt6gS2dr5j4KunIkMSt4=
CodeSize: 1007722
Description: ''
Environment:
  Variables:
    TWILIO_AUTHY_API_KEY: R24pSHJd8eXgqA9XX1zzSV17ytGYw2A3
FunctionArn: arn:aws:lambda:us-east-1:767916421446:function:authy-create-user
FunctionName: authy-create-user
Handler: index.lambda_handler
LastModified: 2020-12-04T23:04:43.246+0000
LastUpdateStatus: Successful
MemorySize: 128
RevisionId: 048a90af-adda-408b-a090-0154d4186775
Role: arn:aws:iam::767916421446:role/lambda-access
Runtime: python3.8
State: Active
Timeout: 3
TracingConfig:
  Mode: PassThrough
Version: $LATEST
```

Test the lambda execution:

```sh
$ aws lambda invoke --function-name authy-create-user \
                    --cli-binary-format raw-in-base64-out \
                    --payload '{ "email": "xyz@gmail.com", "phone": "51996770547", "ccode": "55" }' response.json
```
```txt
ExecutedVersion: $LATEST
StatusCode: 200
```
```sh
$ cat response.json
```
```json
{
	"message": "User created successfully.",
	"user": {
			"id": 314250130
		},
	"success": true
}
```

## Deploy API for Usage

Now, let's deploy the API and test it from public access. First, get the API ID:

```sh
$ aws apigateway get-rest-apis
```
```yaml
items:
- apiKeySource: HEADER
  createdDate: '2020-12-04T18:20:14-03:00'
  endpointConfiguration:
    types:
    - REGIONAL
  id: 77ewbsdd6l
  name: authy-api
```

Deploy into a new stage:

```sh
$ aws apigateway create-deployment --rest-api-id 77ewbsdd6l \
                                   --stage-name dev \
                                   --stage-description 'Development Stage' \
                                   --description 'First deployment to the dev stage'
```
```yaml
createdDate: '2020-12-05T03:00:17-03:00'
description: First deployment to the dev stage
id: ul8olb
```

Build up the invoke URL:

```sh
$ export region="us-east-1"
$ export api_id="77ewbsdd6l"
$ export stage_name="dev"
$ export resource_path="/authy"
$ export invoke_url="https://$api_id.execute-api.$region.amazonaws.com/$stage_name$resource_path"
$ echo $invoke_url
```
```txt
https://77ewbsdd6l.execute-api.us-east-1.amazonaws.com/dev/authy
```

Invoke the API:

```sh
$ curl \
--request POST \
--url $invoke_url \
--header "Content-Type: application/json" \
--data '{ "email": "xyz@gmail.com", "phone": "51996770547", "ccode": 55 }'
```
```json
{"message": "User created successfully.", "user": {"id": 314250130}, "success": "true"}
```

Testing a bad request:

```sh
$ curl \
--request POST \
--url $invoke_url \
--header "Content-Type: application/json" \
--data '{ "email": "bademail", "phone": "51996770547", "ccode": 55 }'
```
```json
{"email": "is invalid", "message": "User was not valid"}
```

> NOTE : Of course, we have a clear open API to call freely and there is a need to add authentication.

## Dropping the stack

To terminate all resources, go to AWS Console > CloudFormation and delete the stack or issue an AWS CLI command for that.

## Summary & Next Steps

This is a basic POC that works as a starting point for enhanced authentication for cloud based applications. It uses a serverless approach which follows best practices for modern applications.

Instead of using application frameworks to build up APIs (i.e. Flask or Django for Python apps) it uses out of the box API implementation and controls.

This POC deals with a step-by-step way of implementation, but in reality it must have automated development and deployment stages using Github or AWS source code control services.

Going forward, applications using cloud services, in this case AWS, can evolve implementing other authentication resources and methods, using AWS S3 storage and CLoudFront for presentation layer on edge locations, implement storage mechanisms with AWS DocumentDB and security with AWS Cognito.

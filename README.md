# EC2-Check-Available
The code hosted by this repository aims to create a **AWS Lambda Function** that identifies **Elastic Compute Cloud (EC2)** 
resources you or other AWS users may have left hanging loose on the account.
<br><br>

## :gear: Needed Configurations
In order to have all required permissions to Run properly, you need to create a custom **IAM Role** so that your Lambda Function
is able to access EC2 and CloudWatch without raising permission errors. <br><br>
You can use the following JSON code to customize your Function's Role: <br>
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "cloudwatch:PutMetricData",
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "ec2:DescribeVolumes"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:*:*:*"
            ],
            "Effect": "Allow"
        }
    ]
}
```
<br><br>

## :pencil: Solution Components
To get this solution up and running, after creating the Lambda Function and assigning it the custom Role, 
create a test event using the Function's console page and click 'Test' to run the code for the 1st time. <br>
Doing that, the necessary metrics will be set up in CloudWatch.
> **You can verify that by going to CloudWatch > All Metrics > LambdaMonitoring**

<br>
After that, you'll only need to set up a Alarms using the newly created metrics, monitoring Available resources every time the code is run. 
<br>

> [Click here for information on how to set up CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ConsoleAlarms.html)

import json
import boto3
import datetime

# Defines the region to which the metrics are going to be exported
METRICS_REGION = 'sa-east-1'

# Defines which regions are going to be verified
REGIONS = ['us-east-1', 'sa-east-1']

# Uncomment line 13 if all regions are needed
# (Don't forget to change Lambda's timeout to at least 30 seconds if so)
#REGIONS = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

ec2 = boto3.client('ec2')
ec2Region = 0
cloudwatch = boto3.client('cloudwatch', region_name=METRICS_REGION)
total_volumes = 0
total_eips = 0
total_snapshots = 0
ebs_tags = []
eip_tags = []

def lambda_handler(event, context):
    # Change the value to False if checking for EBS Volumes without tags isn't needed
    debug_tags = True
    global ec2Region
    for r in REGIONS:
        print("[INFO] Starting verification on region:", r)
        try:
            ec2Region = boto3.client('ec2', region_name=r)
            volumes = ec2Region.describe_volumes()
            snapshots = ec2Region.describe_snapshots(
                OwnerIds=['301676479058']
            )
            eips = ec2Region.describe_addresses()
            check_ebs(volumes)
            check_snapshots(snapshots)
            check_eips(eips)
            search_null(debug_tags)
        except Exception as e:
            print("[ERROR]", e)
        print("[INFO] Verification Ended.")
    return send_metrics()

def check_ebs(volumes):
    global total_volumes, ebs_tags, ec2Region
    for volume in volumes['Volumes']:
        checked = False
        volumeId = volume['VolumeId']
        if 'Tags' in volume:
            for tag in volume['Tags']:
                if 'ebs_available' in tag.values():
                    checked = True
        elif volume['State'] == 'available' and 'Tags' not in volume:
            ebs_tags.append("[WARN] Found EBS Volume without Tags: "+str(volumeId))
            checked = True
        if volume['State'] == 'available' and checked == False:
            print("[ALERT] Found Available EBS volume:", volumeId)
            response = ec2Region.create_tags(
                Resources=[
                    volumeId,
                ],
                Tags=[
                    {
                        'Key': 'ebs_available',
                        'Value': datetime.datetime.now().strftime("%d/%m/%y - %H:%M"),
                    },
                ],
            )
            total_volumes += 1

def check_eips(eips):
    global total_eips, eip_tags, ec2Region
    for eip in eips['Addresses']:
        checked = False
        if 'Tags' in eip:
            for tag in eip['Tags']:
                if 'eip_available' in tag.values():
                    checked = True
        elif 'AssociationId' in eip.keys() and 'Tags' not in eip:
            eip_tags.append("[WARN] Found EIP Address without Tags: "+str(eip['AllocationId']))
            checked = True
        if 'AssociationId' not in eip.keys() and checked == False:
            print("[ALERT] Found EIP not in use:", eip['AllocationId'])
            response = ec2Region.create_tags(
                Resources=[
                    eip['AllocationId'],
                ],
                Tags=[
                    {
                        'Key': 'eip_available',
                        'Value': datetime.datetime.now().strftime("%d/%m/%y - %H:%M"),
                    },
                ],
            )
            total_eips += 1

def send_metrics():
    global total_volumes, total_eips, total_snapshots
    try:
        cloudwatch.put_metric_data(
            Namespace='LambdaMonitoring',
            MetricData=[
                {
                    'Dimensions': [
                        {
                            'Name': 'Service',
                            'Value': 'EC2'
                        },
                    ],
                    'MetricName': 'VolumesAvailable',
                    'Value': total_volumes,
                    'Unit': 'Count'
                }
            ]
        )
        print("[EBS] |"+str(total_volumes)+"| available volumes were found")

        cloudwatch.put_metric_data(
            Namespace='LambdaMonitoring',
            MetricData=[
                {
                    'Dimensions': [
                        {
                            'Name': 'Service',
                            'Value': 'EC2'
                            },
                    ],
                    'MetricName': 'UnusedEIPs',
                    'Value': total_eips,
                    'Unit': 'Count'
                }
            ]
        )
        print("[EIP] |"+str(total_eips)+"| eips not in use found")
        print("[SNAPS] |"+str(total_snapshots)+"| snapshots without volume")
    except Exception as e:
        print("[ERROR] When sending metrics to CloudWatch: "+str(e))

def search_null(debug_tags):
    global ebs_tags, eip_tags
    if debug_tags == True:
        for v in ebs_tags:
            print(v)
        print("\n")
        for ip in eip_tags:
            print(ip)
        print("\n")
        print("[EBS] Found |"+str(len(ebs_tags))+"| volumes without tags")
        print("[EIP] Found |"+str(len(eip_tags))+"| addresses without tags")
        
def check_snapshots(snapshots):
    global total_snapshots, ec2Region
    deleted = False
    
    for s in snapshots['Snapshots']:
        try:
            vol = ec2Region.describe_volumes(
                    VolumeIds=[s['VolumeId']]
            )
            deleted = False
        except:
            deleted = True
            total_snapshots += 1
        if deleted != False and :
            response = ec2Region.create_tags(
                Resources=[s['SnapshotId']],
                Tags=[
                    {
                        'Key': 'nullVolume',
                        'Value': datetime.datetime.now().strftime("%d/%m/%y - %H:%M")
                    },
                ]
            )
    print("[ALERT] Snapshots without volumes were tagged")
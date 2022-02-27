import boto3
import time
import datetime
import os

def set_region_tz():
    timezone_var = None
    #print(os.environ)

    time_now = datetime.datetime.now()
    print("Time Now : " + str(time_now))

    try:
        timezone_var = os.environ['REGION_TZ']
        print("Lambda Environment Variable Key REGION_TZ available : " + str(timezone_var))
    except Exception as e:
        timezone_var = os.environ['TZ']
        print("Lambda Environment Variable Key REGION_TZ not available : " + str(timezone_var))
    print("Timezone Var : " + str(timezone_var))

    if timezone_var is None or timezone_var == '':
        timezone = 'UTC'
    else:
        timezone = timezone_var
    print("Timezone : " + str(timezone))

    os.environ['TZ'] = str(timezone)
    time.tzset()
    return

def lambda_handler(event, context):
    flag = False
    set_region_tz()

    time_now = datetime.datetime.now()
    print("Time Now : " + str(time_now))
    week_day = datetime.datetime.now().isoweekday()  # Monday is 1 and Sunday is 7
    time_plus = time_now + datetime.timedelta(minutes=5)
    time_minus = time_now - datetime.timedelta(minutes=5)
    aest_time = format(time_now, '%H:%M')
    print("Week Day : " + str(week_day))
    print("Time Now in HH:MM : " + aest_time)
    max_aest_time = format(time_plus,'%H:%M')
    min_aest_time = format(time_minus,'%H:%M')
    count = 0

    region = os.environ['AWS_REGION']
    print("Region : " + str(region))

    ec2 = boto3.client("ec2", region_name=region)
    description = ec2.describe_instances()

    for instances in description["Reservations"]:
        for instance in instances["Instances"]:
            #print ('instance :- ' + str(instance))
            count = count + 1
            if 'Tags' in instance:
                for tag in instance["Tags"]:
                    if (tag["Key"] == "StopWeekEnd"):
                        StopWeekEnd_TagFound = True
                        stopTime = tag["Value"]
                        print("StopWeekEnd Stop Time : " + stopTime)
                        if (min_aest_time <= stopTime <= max_aest_time and 6 <= week_day <= 7):
                            print('StopWeekEnd schedule matched : ' + instance["InstanceId"])
                            if instance["State"]["Name"] == "running":
                                print("Stopping instance : " + instance["InstanceId"])
                                ec2 = boto3.resource("ec2", region_name=region)
                                instance = ec2.Instance(instance["InstanceId"])
                                instance.stop()
                                flag = True
                            else:
                                print("Instance not in Running state : " + instance["InstanceId"])
                        else:
                            print("StopWeekEnd schedule not matched : " + instance["InstanceId"])
                        break
                    else:
                        StopWeekEnd_TagFound = False

    if not StopWeekEnd_TagFound:
        print("StopWeekEnd Tag Not Found...")

    if not flag:
        print ("Instances not available to stop")
    print("Total Instance Count : " + str(count))

import boto3
from datetime import datetime, timezone
today = datetime.now(timezone.utc)

msg = ''
for profile in boto3.session.Session().available_profiles:
    msg += f'**** User details for the profile: {profile} ****\n'
    session = boto3.Session(profile_name=profile)
    iam = session.client('iam')

    msg2 = ''
    # check the number of pages, if user is more than 100
    pages = iam.get_paginator('list_users')
    for page in pages.paginate():  # iterate through everypage
        for user in page['Users']:  # iterate through each users
            lastused = user.get('PasswordLastUsed')
            # print(user['Arn'],lastused)
            if lastused:
                diff = today - lastused
                if diff.days > 30:  # check if the last used is more than 90 days
                    msg2 += f"User's Arn: {user['Arn']}\nLast Login: {diff}\n\n"
            else:
                diff = 'Never Used'
                msg2 += f"User's Arn: {user['Arn']}\nLast Login: {diff}\n\n"
    if msg2:
        msg += msg2
    else:
        msg += 'No user is there with more than 90 days lag\n\n\n'
print(msg)
sns = boto3.client('sns')
arn = "arn:aws:sns:us-east-1:120027966364:user-login-age"
sns.publish(TopicArn=arn, 
            Message=msg, 
            Subject="User list")

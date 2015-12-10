from python_dashing.core_modules.base import ServerBase
from six.moves.urllib.parse import urlparse
import logging
import boto3

logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)

class Server(ServerBase):
    pass

class ServerMixin:
    def instances_by_region(self):
        ec2 = boto3.client("ec2", "ap-southeast-2")
        regions = [r['RegionName'] for r in ec2.describe_regions()["Regions"]]
        regions = [r for r in regions if not r.startswith("us-gov") and not r.startswith("cn") and not r.startswith("ap-northeast-1")]

        for region in regions:
            instances = []
            region_ec2 = boto3.client("ec2", region)
            reservations = region_ec2.describe_instances()["Reservations"]
            for res in reservations:
                instances.extend(res["Instances"])

            yield region, instances

    def refreshed_trusted_advisor_checks(self, category=None):
        trusted_advisor = boto3.client("support", "us-east-1")
        checks = trusted_advisor.describe_trusted_advisor_checks(language="en")['checks']

        if category:
            checks = [check for check in checks if check['category'] == category]

        for check in checks:
            trusted_advisor.refresh_trusted_advisor_check(checkId=check['id'])

        return checks

    def trusted_advisor_summaries(self, checks):
        trusted_advisor = boto3.client("support", "us-east-1")
        by_id = dict((check['id'], check) for check in checks)
        summaries = trusted_advisor.describe_trusted_advisor_check_summaries(checkIds=list(by_id.keys()))
        for summary in summaries['summaries']:
            yield by_id[summary['checkId']], summary

    def get_s3_object_body(self, url):
        parsed = urlparse(url)
        bucket = parsed.netloc
        key = parsed.path[1:]
        return boto3.resource("s3").Object(bucket, key).get()["Body"].read()

    def make_boto_session(self, account):
        sts = boto3.client("sts")
        arn = "arn:aws:iam::{0}:{1}".format(account, self.role_to_assume)
        creds = sts.assume_role(RoleArn=arn, RoleSessionName="python-dashing")['Credentials']
        return boto3.Session(aws_access_key_id=creds['AccessKeyId'], aws_secret_access_key=creds['SecretAccessKey'], aws_session_token=creds['SessionToken'])

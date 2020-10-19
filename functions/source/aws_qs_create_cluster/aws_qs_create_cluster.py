import logging
import subprocess
import os
import time
import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=True, log_level='DEBUG')

try:
    s3_client = boto3.client('s3')
except Exception as init_exception:
    helper.init_failure(init_exception)


def create_rafay_cluster(api_key,api_secret,rafay_project,rafay_cluster_name,s3_bucket):
    os.environ["RCTL_API_KEY"] = api_key
    os.environ["RCTL_API_SECRET"] = api_secret
    os.environ["RCTL_PROJECT"] = rafay_project
    os.environ["RCTL_REST_ENDPOINT"] = "console.rafay.dev"
    RCTL_CLUSTER_NAME = rafay_cluster_name
    s3_bucket = s3_bucket
    s3_key = RCTL_CLUSTER_NAME + 'bootstrap.yaml'
    # create an imported cluster in Rafay to get bootstrap configuration 
    cluster_cmd = "rctl create cluster imported " + RCTL_CLUSTER_NAME + " -l aws/" + os.environ["AWS_REGION"] + \
                " > /tmp/cluster-bootstrap.yaml"
    try:
        subprocess.call(cluster_cmd, shell=True)
        with open('/tmp/cluster-bootstrap.yaml') as f:
            if 'cluster.rafay.dev' in f.read():
                s3_client.upload_file('/tmp/cluster-bootstrap.yaml', s3_bucket, s3_key)
                time.sleep(30)
                return s3_bucket,s3_key
            else:
                logger.error("cluster creation failed", exc_info=True)
    except Exception as e:
        logger.error(str(e), exc_info=True)

@helper.create
def create(event, _):
    try:
        s3_bucket,s3_key = create_rafay_cluster(event['RAFAY_API_KEY'], event['RAFAY_API_SECRET'], event['RAFAY_PROJECT'],
                                                event['RAFAY_CLUSTER_NAME'], event['s3_bucket'])
        helper.Data['rafay_s3_bucket'] = s3_bucket
        helper.Data['rafay_s3_key'] = s3_key
        return s3_bucket,s3_key
    except Exception:
        logger.error("unexpected error", exc_info=True)
        return "Cluster Creation Failed"


def lambda_handler(event, context):
    helper(event, context)

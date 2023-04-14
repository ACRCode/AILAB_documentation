#!/usr/local/bin/python
import boto3
import os
import uuid
import pydicom
import sys
import io
import argparse

parser = argparse.ArgumentParser('white rabbit')
parser.add_argument('-j', '--jobId', required=True, help='unique job id')
parser.add_argument('-b', '--bucket', required=True, help='s3 bucket to read input from and write back the output')
parser.add_argument('-g', '--gpu', required=False, help='int indicating which gpu to utilize', default=None)

args = parser.parse_args()
job_id = args.job_id
bucket_name = args.bucket
gpu = args.gpu

input_dir = "jobs/%s/input" % job_id
input_csv = "%s/input.csv" % input_dir
output_dir = "jobs/%s/output" % job_id
output_file = "%s/output.json" % output_dir
scratch_dir = "jobs/%s/scratch" % job_id

print ({
    "jobId": job_id,
    "bucket": bucket_name,
    "gpu": gpu,
    "input_dir": input_dir,
    "input_csv": input_csv,
    "output_dir": output_dir,
    "output_file": output_file })

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
print("reading files from %s" % bucket_name)

# todo: do the evaluation and write the outputfile
output = ""
for o in bucket.objects.filter(Prefix=input_dir):
    print (o.key)
    download_id = str(uuid.uuid4())
    item = o.get()
    body = item['Body'].read()
    filev = io.BytesIO(body)
    print (type(filev))
    ds = pydicom.dcmread(filev, force=True)
    for elm in ds.iterall():
        output = output + "%s\n" % str(elm)

output_object = s3.Object(bucket_name=bucket_name, key=output_file)
output_object.put(Body=output)

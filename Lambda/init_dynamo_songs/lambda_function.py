import json
import boto3
import os
import csv
import codecs
import sys
import collections

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

bucket = os.environ['bucket']
keySongs = os.environ['keySongs']
tableSongsName = os.environ['tableSongs']


def lambda_handler(event, context):
   try:
       obj = s3.Object(bucket, keySongs).get()['Body']
   except:
       print("S3 Object could not be opened. Check environment variable. ")
   try:
       table = dynamodb.Table(tableSongsName)
   except:
       print("Error loading DynamoDB table. Check if table was created correctly and environment variable.")

   batch_size = 100
   batch = []

   for row in csv.DictReader(codecs.getreader('utf-8-sig')(obj), delimiter="~", quoting=csv.QUOTE_NONE):
      if len(batch) >= batch_size:
         write_to_dynamo(batch)
         batch.clear()
      batch.append(row)

   if batch:
      write_to_dynamo(batch)

   return {
      'statusCode': 200,
      'body': json.dumps('Uploaded to DynamoDB Table')
   }


def write_to_dynamo(rows):
   try:
      table = dynamodb.Table(tableSongsName)
   except:
      print("Error loading DynamoDB table. Check if table was created correctly and environment variable.")

   try:
      with table.batch_writer() as batch:
         for i in range(len(rows)):
            batch.put_item(
               Item=collections.OrderedDict([('ITEM_ID', rows[i]['ITEM_ID']), ('NAME', rows[i]['NAME']), ('ARTISTS', rows[i]['ARTISTS'])])
            )
   except:
      print("Error executing batch_writer")
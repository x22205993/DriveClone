''' AWS S3 Bucket Integration'''

import boto3
import urllib.parse

session = boto3.Session()

#FIXME: best way to hardcode bucket name
EXPIRATION_TIME = 600
BUCKET_PREFIX = "x22205993-"

s3_client = boto3.client('s3')
def generate_presigned_url(bucket_name, object_key, file_name=None, for_upload=False):
    #FIXME: Refactor also add validation
    bucket_name = add_prefix_to_bucket(bucket_name)
    params = {
        #FIXME: Is this the best way to do this ?
        "Key": str(object_key),
        "Bucket": bucket_name
    }

    if for_upload:
        client_method = "put_object"
        params.update({ 'ContentType': 'application/octet-stream'})
    else:
        if not file_name:
            raise Exception("File Name not present")
        client_method = "get_object"
        params.update({'ResponseContentDisposition': f'attachment; filename="{urllib.parse.quote(file_name)}"'})
    print(params)
    resp = s3_client.generate_presigned_url(
        client_method,
        Params=params,
        ExpiresIn=EXPIRATION_TIME
    )
    #FIXME: Check error response
    return resp

# FIXME: Handle Validations here 
def delete_object(bucket_name, object_key):
    if not bucket_name or not object_key:
        raise Exception("Bucket Name and Object key is required")
    bucket_name = add_prefix_to_bucket(bucket_name)
    # FIXME: Maybe throw error here ?
    response = s3_client.delete_object(
        Bucket=bucket_name,
        Key=str(object_key)) # Key must be string is this how this should be handled ?
    return response

# FIXME: Handle Validations here 
def delete_multiple_objects(bucket_name, object_keys):
    if not bucket_name or not object_keys:
        raise Exception("Bucket Name and Object key is required ")
    bucket_name = add_prefix_to_bucket(bucket_name)
    response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": str(key)} for key in object_keys]})
    return response

def object_exists(bucket_name, object_key):
    if not bucket_name:
        raise Exception("Bucket Name is mandatory")
    bucket_name = add_prefix_to_bucket(bucket_name)
    try:
        response = s3_client.get_object_attributes(
            Bucket=bucket_name,
            Key=object_key,
            ObjectAttributes=["ObjectSize"]
        )
    except s3_client.exceptions.NoSuchKey:
        return False
    return True

def create_bucket(bucket_name):
    if not bucket_name:
        raise Exception("Bucket Name is mandatory")
    bucket_name = BUCKET_PREFIX + bucket_name
    response = s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration={ 'CORSRules': [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET","PUT","POST"],
                "AllowedOrigins": ["*"],
                "ExposeHeaders": []
            }]
        }
    )
    return response

def add_prefix_to_bucket(bucket_name):
    return BUCKET_PREFIX + bucket_name
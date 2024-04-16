''' AWS S3 Bucket Integration'''
import urllib.parse
import boto3
import botocore


aws_secret_access_key = "SaTW+yvnFTvFXC7rWZMKuSbWQjzZWvkobyaU3f4y"  
class IntegrationException(Exception):
    def __init__(self, error=None, message="Integration Error"):
        self.message = message
        self.error_code = ""
        self.error_msg = ""
        if error:
            self.error_code = error.response['Error']['Code']
            self.error_msg = error.response['Error']['Message']
            self.status_code = error.response['ResponseMetadata']['HTTPStatusCode']
        super().__init__(self.message)


EXPIRATION_TIME = 11
BUCKET_NAME = "x22205993-bucket"
BUCKET_PREFIX = "x22205993-"

s3_client = boto3.client('s3')

def generate_presigned_url(object_key, prefix, file_name=None, for_upload=False):
    ''' Generates a presigned url for uploading or downloading file to and from S3 bucket '''
    object_key = add_prefix_to_object_key(object_key, prefix)
    params = {
        "Key": str(object_key),
        "Bucket": BUCKET_NAME
    }

    if for_upload:
        client_method = "put_object"
        params.update({ 'ContentType': 'application/octet-stream'})
    else:
        if not file_name:
            raise IntegrationException("File Name not present")
        client_method = "get_object"
        params.update({'ResponseContentDisposition': 
                       f'attachment; filename="{urllib.parse.quote(file_name)}"'})
    try:
        resp = s3_client.generate_presigned_url(
            client_method,
            Params=params,
            ExpiresIn=EXPIRATION_TIME
        )
    except botocore.exceptions.ClientError as error:
        raise IntegrationException(error, f'Failed to Generate PreSignedUrl for object key - {str(object_key)}') from error
    return resp

def delete_object(object_key, prefix):
    ''' Delete object from S3 bucket '''
    if not object_key or not prefix:
        raise IntegrationException("Prefix and Object key is required")
    object_key = add_prefix_to_object_key(object_key, prefix)
    try:
        response = s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=str(object_key)) 
    except botocore.exceptions.ClientError as error:
        raise IntegrationException(error, f'Failed to delete object for object key - {str(object_key)}') from error
    return response

def delete_multiple_objects(object_keys, prefix):
    ''' Delete Multiple Objects from S3 Bucket in single request'''
    if not prefix or not object_keys:
        raise IntegrationException("Object Prefix and Object key is required ")
    try:
        response = s3_client.delete_objects(
                    Bucket=BUCKET_NAME,
                    Delete={"Objects": [{"Key": add_prefix_to_object_key(key, prefix)} 
                                        for key in object_keys]})
    except botocore.exceptions.ClientError as error:
        raise IntegrationException(error, f'Failure while deleting multiple objects for object keys - {str(object_keys)}') from error
    return response

def object_exists(object_key, prefix):
    ''' Check if Object exists in the speicifed bucket '''
    if not prefix:
        raise IntegrationException("Object Prefix is mandatory")
    object_key = add_prefix_to_object_key(object_key, prefix)
    try:
        s3_client.get_object_attributes(
            Bucket=BUCKET_NAME,
            Key=object_key,
            ObjectAttributes=["ObjectSize"]
        )
    except s3_client.exceptions.NoSuchKey:
        return False
    except botocore.exceptions.ClientError as error:
        raise IntegrationException(error, f'Failed to Get Object attribute for object key - {str(object_key)}') from error
    return True

def create_bucket(bucket_name):
    ''' Create bucket in S3 '''
    if not bucket_name:
        raise IntegrationException("Bucket Name is mandatory")
    bucket_name = BUCKET_PREFIX + bucket_name
    try:
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
    except botocore.exceptions.ClientError as error:
        raise IntegrationException(error, f'Failed to Create Bucket for Bucket Name - {str(bucket_name)}') from error
    return response

def add_prefix_to_object_key(object_key, prefix):
    ''' By Default all the bucket names will be prefixed by the Bucket Prefix '''
    return str(prefix) + "/" + str(object_key) 

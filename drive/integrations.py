import boto3
import urllib.parse


session = boto3.Session()

#FIXME: best way to hardcode bucket name
BUCKET = "x22205993-bucket"
EXPIRATION_TIME = 600

s3_client = boto3.client('s3')
def generate_presigned_url(object_key, file_name=None, for_upload=False):
    #FIXME: Refactor
    client_method = "get_object"
    http_method = "GET"
    if for_upload:
        client_method = "put_object"
        http_method = "PUT"

    params = {
        #FIXME: Is this the best way to do this ?
        "Key": str(object_key),
        "Bucket": BUCKET
    }
    # FIXME: Find a better way to do this 
    if for_upload:
        params.update({ 'ContentType': 'application/octet-stream'})
    else:
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
def delete_object(object_key=None):
    if not object_key:
        return 
    # FIXME: Maybe throw error here ?
    response = s3_client.delete_object(
        Bucket=BUCKET,
        Key=str(object_key)) # Key must be string is this how this should be handled ?
    return response

# FIXME: Handle Validations here 
def delete_multiple_objects(object_keys=None):
    if not object_keys:
        return
    response = s3_client.delete_objects(
                Bucket=BUCKET,
                Delete={"Objects": [{"Key": str(key)} for key in object_keys]})
    return response

def object_exists(object_key):
    print(object_key)
    try:
        response = s3_client.get_object_attributes(
            Bucket=BUCKET,
            Key=object_key,
            ObjectAttributes=["ObjectSize"]
        )
    except s3_client.exceptions.NoSuchKey:
        return False
    return True
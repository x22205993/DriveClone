import boto3

session = boto3.Session()

#FIXME: best way to hardcode bucket name
BUCKET = "x22205993-bucket"
EXPIRATION_TIME = 6000

s3_client = boto3.client('s3')

def generate_presigned_url(object_key, for_upload=False):
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
    print(params)
    resp = s3_client.generate_presigned_url(
        client_method,
        Params=params,
        ExpiresIn=EXPIRATION_TIME,
        HttpMethod=http_method
    )
    #FIXME: Check error response
    return resp


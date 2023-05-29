import os

DEFAULT_FILE_STORAGE = 'errander.cdn.backends.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'errander.cdn.backends.StaticRootS3BotoStorage'

LINODE_BUCKET_REGION = 'eu-central-1'


AWS_S3_ENDPOINT_URL = 'https://eu-central-1.linodeobjects.com'
AWS_ACCESS_KEY_ID = os.environ.get('LINODE_BUCKET_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('LINODE_BUCKET_SECRET_KEY')
AWS_S3_REGION_NAME = LINODE_BUCKET_REGION
AWS_S3_USE_SSL = True
AWS_STORAGE_BUCKET_NAME = 'errander'

import api
import ui
from config import app
from minio import Minio
from uvicorn import run

import pymongo

# myclient = pymongo.MongoClient('mongodb', 27017)
#
# data = myclient.details
# storage = data.storage
# status = storage.insert_one({
#     "kakashka" : "bugagashka))"
# })
# print(status)

# client = Minio(
#     "minio:9000",
#     access_key="8BCE0pL40rhjDqlAll00",
#     secret_key="t2l9rTFKP1G2ahZ6EKrahKHX8tBdZkxtQE0tgges",
#     secure=False
# )
# client.make_bucket("my-bucket")
# buckets = client.list_buckets()
# for bucket in buckets:
#     print(bucket.name, bucket.creation_date)

# if __name__ == '__main__':
#     run('config:app')

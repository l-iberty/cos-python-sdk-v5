# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_comm import get_md5, to_bytes

import sys
import os
import logging
import base64

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-beijing'      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 服务端加密必须使用 https

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)  # 获取配置对象
client = CosS3Client(config)

# 上传 SSE-COS 加密对象，指定加密类型为 AES256即为 SSE-COS 加密
response = client.put_object(
    Bucket='examplebucket-125000000',
    Key='sdk-sse-cos',
    Body='123',
    ServerSideEncryption='AES256' 
)
print(response['x-cos-server-side-encryption']) # 服务端返回'x-cos-server-side-encryption': 'AES256' 表示是 SSE-COS 对象

# 下载 SSE-COS 加密对象，不需要携带加密头域，由服务端自动解密
response = client.get_object(
    Bucket='examplebucket-125000000',
    Key='sdk-sse-cos'
)
print(response['x-cos-server-side-encryption']) # 服务端返回'x-cos-server-side-encryption': 'AES256' 表示是 SSE-COS 对象


# 上传 SSE-KMS 加密对象，指定加密类型为 cos/kms 即为 SSE-KMS 加密
response = client.put_object(
    Bucket='examplebucket-125000000',
    Key='sdk-sse-kms',
    Body='123',
    ServerSideEncryption='cos/kms',  # SSE-KMS 加密固定填写 cos/kms
    SSEKMSKeyId='kms-key-id',  # 填写 KMS 的用户主密钥 CMK，如不填写则使用 COS 默认创建的 CMK
    SSEKMSContext=base64.standard_b64encode(to_bytes("{\"test\":\"test\"}")) # 加密上下文，值为 JSON 格式加密上下文键值对的 Base64 编码，可选
)
print(response['x-cos-server-side-encryption']) # 服务端返回'x-cos-server-side-encryption': 'cos/kms' 表示是 SSE-KMS 对象

# 下载 SSE-KMS 加密对象，不需要携带加密头域，由服务端自动解密
response = client.get_object(
    Bucket='examplebucket-125000000',
    Key='sdk-sse-kms'
)
print(response['x-cos-server-side-encryption']) # 服务端返回'x-cos-server-side-encryption': 'cos/kms' 表示是 SSE-KMS 对象

# 高级接口上传 SSE-KMS 加密对象，指定加密类型为 cos/kms 即为 SSE-KMS 加密
response = client.upload_file(
    Bucket='examplebucket-125000000', 
    Key='sdk-sse-kms', 
    LocalFilePath="sdk-sse-kms.local", 
    ServerSideEncryption='cos/kms') # SSE-KMS 加密固定填写 cos/kms

# 高级接口下载 SSE-KMS 加密对象，不需要携带加密头域，由服务端自动解密
response = client.download_file(
    Bucket='examplebucket-125000000', 
    Key='sdk-sse-kms', 
    DestFilePath='sdk-sse-kms.local')

# 上传、下载、拷贝、取回 SSE-C 加密对象

bucket = 'examplebucket-125000000'
file_name = 'sdk-sse-c'

# 编码和哈希加密密钥
ssec_secret = '00000000000000000000000000000001' # 原始密钥需要是32位
ssec_key = base64.standard_b64encode(to_bytes(ssec_secret)) # 密钥必须 Base64编码
ssec_key_md5 = get_md5(ssec_secret)

# 上传 SSE-C 加密对象
response = client.put_object(
    Bucket=bucket, Key=file_name, Body="00000",
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)
print(response['x-cos-server-side-encryption-customer-algorithm']) # 服务端返回'x-cos-server-side-encryption-customer-algorithm': 'AES256' 表示是 SSE-C 对象

# 下载 SSE-C 加密对象
response = client.get_object(
    Bucket=bucket, Key=file_name,
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)
print(response['x-cos-server-side-encryption-customer-algorithm']) # 服务端返回'x-cos-server-side-encryption-customer-algorithm': 'AES256' 表示是 SSE-C 对象

# HEAD SSE-C 加密对象
response = client.head_object(
    Bucket=bucket, Key=file_name, 
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)
print(response['x-cos-server-side-encryption-customer-algorithm']) # 服务端返回'x-cos-server-side-encryption-customer-algorithm': 'AES256' 表示是 SSE-C 对象

# 高级接口上传 SSE-C 加密对象
response = client.upload_file(
    Bucket=bucket, Key=file_name, LocalFilePath="sdk-sse-c.local",
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)

# 高级接口下载 SSE-C 加密对象
response = client.download_file(
    Bucket=bucket, Key=file_name, DestFilePath='sdk-sse-c.local',
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)

# 拷贝 SSE-C 加密对象，源和目标的加密类型和密钥可以不一样。例子中的源对象是 SSE-C 类型，目标对象也是 SSE-C 类型。
dest_ssec_secret = '00000000000000000000000000000002' # 密钥需要是32位
dest_ssec_key = base64.standard_b64encode(to_bytes(dest_ssec_secret))
dest_ssec_key_md5 = get_md5(dest_ssec_secret)
copy_source = {'Bucket': bucket, 'Key': file_name, 'Region': region}
response = client.copy_object(
    Bucket=bucket, Key='sdk-sse-c-copy', CopySource=copy_source,
    SSECustomerAlgorithm='AES256', SSECustomerKey=dest_ssec_key, SSECustomerKeyMD5=dest_ssec_key_md5,
    CopySourceSSECustomerAlgorithm='AES256', CopySourceSSECustomerKey=ssec_key, CopySourceSSECustomerKeyMD5=ssec_key_md5
)

# 高级接口拷贝 SSE-C 加密对象
response = client.copy(
    Bucket=bucket, Key='sdk-sse-c-copy', CopySource=copy_source, MAXThread=2,
    SSECustomerAlgorithm='AES256', SSECustomerKey=dest_ssec_key, SSECustomerKeyMD5=dest_ssec_key_md5,
    CopySourceSSECustomerAlgorithm='AES256', CopySourceSSECustomerKey=ssec_key, CopySourceSSECustomerKeyMD5=ssec_key_md5)

# 取回 SSE-C 加密对象
response = client.restore_object(
    Bucket=bucket, Key=file_name, RestoreRequest={
        'Days': 1,
        'CASJobParameters': {
            'Tier': 'Expedited'
        }
    }, 
    SSECustomerAlgorithm='AES256', SSECustomerKey=ssec_key, SSECustomerKeyMD5=ssec_key_md5)
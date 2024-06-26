# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_encryption_client import CosEncryptionClient
from qcloud_cos.crypto import AESProvider, RSAKeyPair
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-beijing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048

conf = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)

'''使用对称 AES256 加密每次生成的随机密钥示例
'''

# 方式一：通过密钥值初始化加密客户端
# 注意：按照 AES 算法的要求，aes_key_value 需为 base64编码后的结果
aes_provider = AESProvider(aes_key='aes_key_value')

# 方式二：通过密钥路径初始化加密客户端
aes_key_pair = AESProvider(aes_key_path='aes_key_path')

client_for_aes = CosEncryptionClient(conf, aes_provider)

# 上传对象，兼容非加密客户端的 put_object 的所有功能，具体使用可参考 put_object
response = client_for_aes.put_object(
                        Bucket='examplebucket-1250000000',
                        Body=b'bytes',
                        Key='exampleobject',
                        EnableMD5=False)

# 下载对象，兼容非加密客户端的 get_object 的所有功能，具体使用可参考 get_object
response = client_for_aes.get_object(
                        Bucket='examplebucket-1250000000',
                        Key='exampleobject')

# 分块上传，兼容非加密客户端的分块上传，除了最后一个part，每个 part 的大小必须为16字节的整数倍
response = client_for_aes.create_multipart_upload(
                        Bucket='examplebucket-1250000000',
                        Key='exampleobject_upload')
uploadid = response['UploadId']
client_for_aes.upload_part(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                Body=b'bytes',
                PartNumber=1,
                UploadId=uploadid)
response = client_for_aes.list_parts(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                UploadId=uploadid)
client_for_aes.complete_multipart_upload(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                UploadId=uploadid,
                MultipartUpload={'Part':response['Part']})

# 断点续传方式上传对象，`partsize`大小必须为16字节的整数倍
response = client_for_aes.upload_file(
    Bucket='test04-123456789',
    LocalFilePath='local.txt',
    Key='exampleobject',
    PartSize=10,
    MAXThread=10
)

'''使用非对称 RSA 加密每次生成的随机密钥示例
'''

# 方式一：通过密钥值初始化加密客户端
rsa_key_pair = RSAProvider.get_rsa_key_pair('public_key_value', 'private_key_value')

# 方式二：通过密钥路径初始化加密客户端
rsa_key_pair = RSAProvider.get_rsa_key_pair_path('public_key_path', 'private_key_path')

rsa_provider = RSAProvider(key_pair_info=rsa_key_pair)
client_for_rsa = CosEncryptionClient(conf, rsa_provider)

# 上传对象，兼容非加密客户端的 put_object 的所有功能，具体使用可参考 put_object
response = client_for_rsa.put_object(
                        Bucket='examplebucket-1250000000',
                        Body=b'bytes',
                        Key='exampleobject',
                        EnableMD5=False)

# 下载对象，兼容非加密客户端的 get_object 的所有功能，具体使用可参考 get_object
response = client_for_rsa.get_object(
                        Bucket='examplebucket-1250000000',
                        Key='exampleobject')

# 分块上传，兼容非加密客户端的分块上传，除了最后一个 part，每个 part 的大小必须为16字节的整数倍
response = client_for_rsa.create_multipart_upload(
                        Bucket='examplebucket-1250000000',
                        Key='exampleobject_upload')
uploadid = response['UploadId']
client_for_rsa.upload_part(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                Body=b'bytes',
                PartNumber=1,
                UploadId=uploadid)
response = client_for_rsa.list_parts(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                UploadId=uploadid)
client_for_rsa.complete_multipart_upload(
                Bucket='examplebucket-1250000000',
                Key='exampleobject_upload',
                UploadId=uploadid,
                MultipartUpload={'Part':response['Part']})

# 断点续传方式上传对象，`partsize`大小必须为16字节的整数倍
response = client_for_rsa.upload_file(
    Bucket='test04-123456789',
    LocalFilePath='local.txt',
    Key='exampleobject',
    PartSize=10,
    MAXThread=10
)
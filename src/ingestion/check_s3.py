import os
import boto3
from dotenv import load_dotenv

# Загружаем ключи из нашего файла .env
load_dotenv(dotenv_path="containers/.env")

print("🔍 Connecting to S3 Garage for direct inspection...")

# Инициализируем клиент с жесткими таймаутами
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

try:
    # Запрашиваем у Garage прямой список всех объектов внутри бакета
    response = s3_client.list_objects_v2(Bucket='lambda-bronze')
    
    if 'Contents' in response:
        print(f"🎉 Success! Found {len(response['Contents'])} files inside lambda-bronze:\n")
        for obj in response['Contents']:
            print(f"📄 File: {obj['Key']} (Size: {obj['Size']} Bytes)")
    else:
        print("📁 Bucket 'lambda-bronze' is completely empty.")
        
except Exception as e:
    print(f"❌ Failed to inspect S3 Lake: {e}")

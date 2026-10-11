import os
import json
import time
from datetime import datetime
import uuid
import boto3
from kafka import KafkaConsumer
from dotenv import load_dotenv
import logging
import sys

load_dotenv(dotenv_path="containers/.env")

KAFKA_BOOTSTRAP_SERVER = "127.0.0.1:9094"
KAFKA_TOPIC = "snowplow_web_events"
BATCH_SIZE = 50
BATCH_TIMEOUT_SEC = 10


print("🐋 Starting S3 Bronze Ingestion Worker...")
print(f"Reading from Kafka: {KAFKA_BOOTSTRAP_SERVER} -> Topic: {KAFKA_TOPIC}")


s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='s3_bronze_ingestor_group_prod',
    enable_auto_commit=False,
    api_version=(3, 7, 0),
    check_crcs=False,
    
    # ИДЕАЛЬНЫЙ ТРЕНД ТАЙМАУТОВ: каждый следующий параметр СТРОГО больше предыдущего
    fetch_max_wait_ms=500,          # 0.5 сек (ожидание накопления батча на стороне брокера)
    session_timeout_ms=10000,       # 10 сек (время жизни сессии консьюмера)
    request_timeout_ms=15000,       # 15 сек (сетевой таймаут запроса - ТЕПЕРЬ ОН БОЛЬШЕ СЕССИИ!)
    connections_max_idle_ms=30000   # 30 сек (максимальный простой соединения)
)

def upload_batch_to_s3(batch_data):

    if not batch_data:
        return False
        
    now = datetime.utcnow()
    # bronze/year=2026/month=10/day=11/
    s3_key = f"year={now.year}/month={now.strftime('%m')}/day={now.strftime('%d')}/{uuid.uuid4()}.json"
    
    file_content = "\n".join([json.dumps(msg) for msg in batch_data])
    
    try:
        s3_client.put_object(
            Bucket='lambda-bronze',
            Key=s3_key,
            Body=file_content
        )
        print(f"💾 Successfully uploaded {len(batch_data)} events to S3: lambda-bronze/{s3_key}")
        return True
    except Exception as e:
        print(f"❌ Failed to upload to S3: {e}")
        return False


try:
    current_batch = []
    last_flush_time = time.time()
    
    while True:
        try:
            # Запрашиваем данные у Кафки
            msg_pack = consumer.poll(timeout_ms=500)
            
            # Если данные прилетели, распаковываем их в наш батч
            for tp, messages in msg_pack.items():
                for message in messages:
                    current_batch.append(message.value)
                    
        except ValueError as selector_err:
            # Ловим баг дескриптора -1 на Windows, пишем предупреждение и просто идем дальше!
            # На следующем витке цикла библиотека автоматически восстановит сокет.
            if "Invalid file descriptor: -1" in str(selector_err):
                print("⚠️ Windows Selector glitch caught (-1). Reconnecting socket automatically...", end="\r")
                time.sleep(0.5)
                continue
            else:
                raise selector_err
        
        # Проверка времени и отправка в S3 (оставляем без изменений)
        time_since_last_flush = time.time() - last_flush_time
        
        if len(current_batch) >= BATCH_SIZE or (time_since_last_flush >= BATCH_TIMEOUT_SEC and len(current_batch) > 0):
            if upload_batch_to_s3(current_batch):
                consumer.commit()
                current_batch = []
                last_flush_time = time.time()
                
        time.sleep(0.1)
                
except KeyboardInterrupt:
    print("\n🛑 Ingestion worker stopped.")
    if current_batch:
        print("Saving remaining messages before exit...")
        upload_batch_to_s3(current_batch)
        consumer.commit()
    consumer.close()

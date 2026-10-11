import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVER = "127.0.0.1:9094"
KAFKA_TOPIC = "snowplow_web_events"

print("🚀 Starting Production-Ready Direct Kafka Traffic Generator...")
print(f"Connecting to Broker: {KAFKA_BOOTSTRAP_SERVER}")
print(f"Target Topic: {KAFKA_TOPIC}\nPress Ctrl+C to stop.\n")

try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3
    )
except Exception as e:
    print(f"❌ Failed to connect to Kafka Broker: {e}")
    exit(1)

PRODUCTS = [
    {"id": "prod_111", "name": "Wireless Headphones", "price": 99.99},
    {"id": "prod_222", "name": "Mechanical Keyboard", "price": 149.50},
    {"id": "prod_333", "name": "Ergonomic Mouse", "price": 79.00},
    {"id": "prod_444", "name": "4K Monitor", "price": 380.00},
]

MARKETING_CHANNELS = ["google", "yandex", "telegram"]

def generate_user_session():
    return {
        "user_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "utm_source": random.choice(MARKETING_CHANNELS),
        "ab_group": random.choice(["A", "B"])
    }

def send_direct_to_kafka(event_type, user_ctx, payload):
    
    if user_ctx["ab_group"] == "B":
        page_load_time = int(random.normalvariate(350, 50))
    else:
        page_load_time = int(random.normalvariate(800, 150))

    event_message = {
        "event_id": str(uuid.uuid4()),
        "event_time": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_ctx["user_id"],
        "session_id": user_ctx["session_id"],
        "utm_source": user_ctx["utm_source"],
        "ab_test_variant": user_ctx["ab_group"],
        "page_load_time_ms": max(50, page_load_time),
        "payload": payload
    }

    try:
        producer.send(KAFKA_TOPIC, value=event_message)
        return True
    except Exception as e:
        print(f"❌ Error pushing to Kafka: {e}")
        return False

try:
    active_sessions = [generate_user_session() for _ in range(10)]
    
    while True:
        if random.random() < 0.2:
            user = generate_user_session()
            active_sessions.pop(0)
            active_sessions.append(user)
        else:
            user = random.choice(active_sessions)

        action = random.random()
        
        if action < 0.5:
            send_direct_to_kafka("page_view", user, {"url": "/home"})
            print(f"👁️ User [{user['user_id'][:8]}] (Group {user['ab_group']}) viewed page view")
            
        elif action < 0.8:
            prod = random.choice(PRODUCTS)
            send_direct_to_kafka("product_view", user, {"product_id": prod["id"], "price": prod["price"]})
            print(f"📦 User [{user['user_id'][:8]}] viewed product: {prod['name']}")
            
        elif action < 0.95:
            prod = random.choice(PRODUCTS)
            send_direct_to_kafka("add_to_cart", user, {"product_id": prod["id"], "quantity": 1})
            print(f"🛒 User [{user['user_id'][:8]}] added to cart: {prod['name']}")
            
        else:
            prod = random.choice(PRODUCTS)
            send_direct_to_kafka("purchase", user, {
                "order_id": str(random.randint(100000, 999999)), 
                "total_price": prod["price"]
            })
            print(f"💰💰💰 User [{user['user_id'][:8]}] PURCHASED: {prod['name']}!")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Traffic generator stopped. Flushing pending messages...")
    producer.flush()
    print("Done.")

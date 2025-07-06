"""
Event based Arch
======================
Event producer - > API 
Event channels  ->   Kafka , rabbit mq 
event consumers  -> 
event routers ->  kafka strems 
event stroed -> eventstoreDB
event pricessig engine - process complext event 

"""
from kafka import KafkaProducer,KafkaConsumer
import json

producer = KafkaProducer(bootstrap_servers ='localhost:9092',value_serializer=lambda v:json.dumps(v))

event = {"event_type":"TradeExecuted","symbol":"AAPL","price":150}

consumer = KafkaConsumer('trade-events',
                        bootstrap_servers ='localhost:9092',
                        value_deserializer=lambda v:json.loads(v.decode('utf-8'))
                        )

for event in consumer:
    print(event.value)


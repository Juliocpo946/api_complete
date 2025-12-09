import pika
import json
from typing import Dict, Any
from src.infrastructure.config.rabbitmq_config import rabbitmq_config

class RabbitMQPublisher:
    
    @staticmethod
    def publish_event(routing_key: str, message: Dict[str, Any]):
        try:
            params = pika.URLParameters(rabbitmq_config.RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.exchange_declare(
                exchange=rabbitmq_config.EXCHANGE_NAME,
                exchange_type='topic',
                durable=True
            )
            
            channel.basic_publish(
                exchange=rabbitmq_config.EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            connection.close()
            
            print(f"\n[RABBITMQ] Evento publicado: {routing_key}")
            print(f"Mensaje: {message}")
            
        except Exception as e:
            print(f"\n[RABBITMQ ERROR] No se pudo publicar evento: {e}")
    
    @staticmethod
    def publish_activity_paused(activity_uuid: str, session_id: str):
        RabbitMQPublisher.publish_event(
            "activity.paused",
            {
                "activity_uuid": activity_uuid,
                "session_id": session_id,
                "event": "paused",
                "timestamp": None
            }
        )
    
    @staticmethod
    def publish_activity_resumed(activity_uuid: str, session_id: str):
        RabbitMQPublisher.publish_event(
            "activity.resumed",
            {
                "activity_uuid": activity_uuid,
                "session_id": session_id,
                "event": "resumed",
                "timestamp": None
            }
        )
    
    @staticmethod
    def publish_activity_completed(activity_uuid: str, session_id: str):
        RabbitMQPublisher.publish_event(
            "activity.completed",
            {
                "activity_uuid": activity_uuid,
                "session_id": session_id,
                "event": "completed",
                "timestamp": None
            }
        )
    
    @staticmethod
    def publish_activity_abandoned(activity_uuid: str, session_id: str):
        RabbitMQPublisher.publish_event(
            "activity.abandoned",
            {
                "activity_uuid": activity_uuid,
                "session_id": session_id,
                "event": "abandoned",
                "timestamp": None
            }
        )
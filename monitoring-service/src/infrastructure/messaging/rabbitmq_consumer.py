import pika
import json
import threading
from typing import Callable
from src.infrastructure.config.rabbitmq_config import rabbitmq_config

class RabbitMQConsumer:
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.connection = None
        self.channel = None
        self.thread = None
        self.is_running = False
    
    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._consume, daemon=True)
        self.thread.start()
        print("\n[RABBITMQ] Consumidor iniciado")
    
    def stop(self):
        self.is_running = False
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        print("\n[RABBITMQ] Consumidor detenido")
    
    def _consume(self):
        try:
            params = pika.URLParameters(rabbitmq_config.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            self.channel.exchange_declare(
                exchange=rabbitmq_config.EXCHANGE_NAME,
                exchange_type='topic',
                durable=True
            )
            
            result = self.channel.queue_declare(
                queue=rabbitmq_config.QUEUE_NAME,
                durable=True
            )
            queue_name = result.method.queue
            
            for routing_key in rabbitmq_config.ROUTING_KEYS:
                self.channel.queue_bind(
                    exchange=rabbitmq_config.EXCHANGE_NAME,
                    queue=queue_name,
                    routing_key=routing_key
                )
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message,
                auto_ack=False
            )
            
            print(f"\n[RABBITMQ] Esperando mensajes en cola: {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            print(f"\n[RABBITMQ ERROR] Error en consumidor: {e}")
            if self.is_running:
                print("[RABBITMQ] Reintentando conexión en 5 segundos...")
                import time
                time.sleep(5)
                if self.is_running:
                    self._consume()
    
    def _on_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            routing_key = method.routing_key
            
            print(f"\n[RABBITMQ] Mensaje recibido: {routing_key}")
            print(f"Contenido: {message}")
            
            self.callback(routing_key, message)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"\n[RABBITMQ ERROR] Error procesando mensaje: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
import os
from dotenv import load_dotenv

load_dotenv()

class RabbitMQConfig:
    RABBITMQ_URL = os.getenv(
        "RABBITMQ_URL",
        "amqps://siptuvyg:BZ2HUpBpSm_NNkGuRJYMviNrvLGYu7lm@gorilla.lmq.cloudamqp.com/siptuvyg"
    )
    EXCHANGE_NAME = "activity_events"

rabbitmq_config = RabbitMQConfig()
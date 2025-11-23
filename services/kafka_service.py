"""
Kafka event streaming service.

Provides producers and consumers for event-driven architecture.
"""

import os
import json
import logging
from typing import Any, Callable, Optional
from datetime import datetime

try:
    from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
    from confluent_kafka.admin import AdminClient, NewTopic
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    Producer = None
    Consumer = None

logger = logging.getLogger(__name__)


# Default topics for the platform
TOPICS = {
    "signals": "platform.signals",
    "events": "platform.events",
    "commands": "platform.commands",
    "metrics": "platform.metrics",
    "alerts": "platform.alerts",
    "audit": "platform.audit",
}


class KafkaProducerService:
    """Kafka producer for publishing events."""

    def __init__(
        self,
        bootstrap_servers: str = None,
        client_id: str = "dev-platform-producer"
    ):
        if not KAFKA_AVAILABLE:
            raise ImportError(
                "confluent-kafka not installed. "
                "Install with: pip install confluent-kafka"
            )

        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"
        )

        self._producer = Producer({
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": client_id,
            "acks": "all",
            "retries": 3,
            "retry.backoff.ms": 1000,
        })

    def _delivery_callback(self, err, msg):
        """Callback for message delivery reports."""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(
                f"Message delivered to {msg.topic()} [{msg.partition()}] "
                f"at offset {msg.offset()}"
            )

    def produce(
        self,
        topic: str,
        value: dict,
        key: str = None,
        headers: dict = None,
        callback: Callable = None
    ):
        """
        Produce a message to a Kafka topic.

        Args:
            topic: Topic name (can use TOPICS keys like "signals")
            value: Message payload (will be JSON serialized)
            key: Optional message key for partitioning
            headers: Optional message headers
            callback: Optional delivery callback
        """
        # Resolve topic name
        resolved_topic = TOPICS.get(topic, topic)

        # Serialize value
        serialized = json.dumps(value).encode("utf-8")

        # Prepare headers
        kafka_headers = None
        if headers:
            kafka_headers = [(k, v.encode("utf-8")) for k, v in headers.items()]

        # Produce message
        self._producer.produce(
            topic=resolved_topic,
            value=serialized,
            key=key.encode("utf-8") if key else None,
            headers=kafka_headers,
            callback=callback or self._delivery_callback
        )

        # Trigger delivery callbacks
        self._producer.poll(0)

    def produce_signal(self, signal: dict):
        """Produce a signal event."""
        self.produce(
            topic="signals",
            value=signal,
            key=signal.get("source", {}).get("node_ref"),
            headers={
                "event_type": signal.get("type", "unknown"),
                "correlation_id": signal.get("correlation_id", ""),
            }
        )

    def produce_metric(
        self,
        name: str,
        value: float,
        tags: dict = None,
        timestamp: datetime = None
    ):
        """Produce a metric event."""
        metric = {
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        }
        self.produce(
            topic="metrics",
            value=metric,
            key=name
        )

    def produce_alert(
        self,
        severity: str,
        summary: str,
        source: str,
        detail: str = None
    ):
        """Produce an alert event."""
        alert = {
            "severity": severity,
            "summary": summary,
            "source": source,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.produce(
            topic="alerts",
            value=alert,
            key=source
        )

    def flush(self, timeout: float = 10.0):
        """Flush pending messages."""
        self._producer.flush(timeout)

    def close(self):
        """Close the producer."""
        self.flush()


class KafkaConsumerService:
    """Kafka consumer for subscribing to events."""

    def __init__(
        self,
        bootstrap_servers: str = None,
        group_id: str = "dev-platform-consumer",
        auto_offset_reset: str = "earliest"
    ):
        if not KAFKA_AVAILABLE:
            raise ImportError(
                "confluent-kafka not installed. "
                "Install with: pip install confluent-kafka"
            )

        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"
        )

        self._consumer = Consumer({
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": True,
            "auto.commit.interval.ms": 5000,
        })

        self._running = False
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, topics: list[str]):
        """
        Subscribe to topics.

        Args:
            topics: List of topic names (can use TOPICS keys)
        """
        resolved = [TOPICS.get(t, t) for t in topics]
        self._consumer.subscribe(resolved)
        logger.info(f"Subscribed to topics: {resolved}")

    def add_handler(self, topic: str, handler: Callable[[dict], None]):
        """
        Add a message handler for a topic.

        Args:
            topic: Topic name
            handler: Function to call with deserialized message
        """
        resolved = TOPICS.get(topic, topic)
        if resolved not in self._handlers:
            self._handlers[resolved] = []
        self._handlers[resolved].append(handler)

    def consume(self, timeout: float = 1.0) -> Optional[dict]:
        """
        Consume a single message.

        Returns:
            Deserialized message or None if no message available
        """
        msg = self._consumer.poll(timeout)

        if msg is None:
            return None

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                return None
            raise KafkaException(msg.error())

        # Deserialize
        value = json.loads(msg.value().decode("utf-8"))

        # Extract headers
        headers = {}
        if msg.headers():
            headers = {k: v.decode("utf-8") for k, v in msg.headers()}

        return {
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "key": msg.key().decode("utf-8") if msg.key() else None,
            "value": value,
            "headers": headers,
            "timestamp": msg.timestamp()[1],
        }

    def run(self, poll_timeout: float = 1.0):
        """
        Run the consumer loop.

        Continuously polls for messages and dispatches to handlers.
        """
        self._running = True
        logger.info("Starting consumer loop...")

        try:
            while self._running:
                message = self.consume(poll_timeout)

                if message:
                    topic = message["topic"]
                    handlers = self._handlers.get(topic, [])

                    for handler in handlers:
                        try:
                            handler(message["value"])
                        except Exception as e:
                            logger.error(
                                f"Handler error for {topic}: {e}"
                            )

        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        finally:
            self.close()

    def stop(self):
        """Stop the consumer loop."""
        self._running = False

    def close(self):
        """Close the consumer."""
        self._consumer.close()


class KafkaAdminService:
    """Kafka admin operations."""

    def __init__(self, bootstrap_servers: str = None):
        if not KAFKA_AVAILABLE:
            raise ImportError(
                "confluent-kafka not installed. "
                "Install with: pip install confluent-kafka"
            )

        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"
        )

        self._admin = AdminClient({
            "bootstrap.servers": self.bootstrap_servers
        })

    def create_topics(
        self,
        topics: list[str] = None,
        num_partitions: int = 3,
        replication_factor: int = 1
    ):
        """
        Create topics if they don't exist.

        Args:
            topics: List of topic names (defaults to all TOPICS)
            num_partitions: Number of partitions per topic
            replication_factor: Replication factor
        """
        if topics is None:
            topics = list(TOPICS.values())
        else:
            topics = [TOPICS.get(t, t) for t in topics]

        # Get existing topics
        existing = set(self._admin.list_topics().topics.keys())

        # Create missing topics
        new_topics = []
        for topic in topics:
            if topic not in existing:
                new_topics.append(NewTopic(
                    topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                ))

        if new_topics:
            futures = self._admin.create_topics(new_topics)
            for topic, future in futures.items():
                try:
                    future.result()
                    logger.info(f"Created topic: {topic}")
                except Exception as e:
                    logger.error(f"Failed to create topic {topic}: {e}")

    def list_topics(self) -> list[str]:
        """List all topics."""
        return list(self._admin.list_topics().topics.keys())

    def delete_topics(self, topics: list[str]):
        """Delete topics."""
        resolved = [TOPICS.get(t, t) for t in topics]
        futures = self._admin.delete_topics(resolved)

        for topic, future in futures.items():
            try:
                future.result()
                logger.info(f"Deleted topic: {topic}")
            except Exception as e:
                logger.error(f"Failed to delete topic {topic}: {e}")


# Global instances
_producer = None
_consumer = None


def get_kafka_producer() -> KafkaProducerService:
    """Get the global Kafka producer instance."""
    global _producer
    if _producer is None:
        _producer = KafkaProducerService()
    return _producer


def get_kafka_consumer(group_id: str = "dev-platform") -> KafkaConsumerService:
    """Get a Kafka consumer instance."""
    return KafkaConsumerService(group_id=group_id)


def produce_signal(signal: dict):
    """Convenience function to produce a signal."""
    get_kafka_producer().produce_signal(signal)


def produce_metric(name: str, value: float, tags: dict = None):
    """Convenience function to produce a metric."""
    get_kafka_producer().produce_metric(name, value, tags)


def produce_alert(severity: str, summary: str, source: str, detail: str = None):
    """Convenience function to produce an alert."""
    get_kafka_producer().produce_alert(severity, summary, source, detail)


def init_kafka_topics():
    """Initialize all platform topics."""
    admin = KafkaAdminService()
    admin.create_topics()

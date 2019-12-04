import logging
import os
import time
import uuid

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, KafkaError, TopicPartition


class KafkaClient:

    def __init__(self, brokers: list, username: str, password: str):
        self.brokers = brokers
        self.username = username
        self.password = password
        self.group_id = str(uuid.uuid1())

    def get_config(self):
        config = {'bootstrap.servers': ','.join(self.brokers),
                  'group.id': self.group_id,
                  'default.topic.config': {'auto.offset.reset': 'earliest'},
                  'enable.auto.commit': False
                  }

        # append Event streams specific config
        config.update({'ssl.ca.location': '/etc/ssl/certs/',
                       'sasl.mechanisms': 'PLAIN',
                       'sasl.username': self.username,
                       'sasl.password': self.password,
                       'security.protocol': 'sasl_ssl'
                       })
        return config

    def create_consumer(self, topic):
        """
        Creates a new kafka consumer
        """
        config = self.get_config()
        consumer = Consumer(config)
        consumer.subscribe([topic])
        logging.info("Now listening on topic: {}".format(topic))
        return consumer

    def create_topic(self, topic):
        """
        Create topics
        """
        config = self.get_config()
        admin_clinet = AdminClient(config)

        new_topic = [NewTopic(topic, num_partitions=3, replication_factor=3)]
        # Call create_topics to asynchronously create topics, a dict
        # of <topic,future> is returned.
        fs = admin_clinet.create_topics(new_topic)

        # Wait for operation to finish.
        # Timeouts are preferably controlled by passing request_timeout=15.0
        # to the create_topics() call.
        # All futures will finish at the same time.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                logging.info("Topic {} created".format(topic))
                return True
            except Exception as e:
                logging.info("Failed to create topic {}: {}".format(topic, e))
                return False
    
    def delete_topic(self, topic):
        """
        delete a topic
        """
        # Call delete_topics to asynchronously delete topics, a future is returned.
        # By default this operation on the broker returns immediately while
        # topics are deleted in the background. But here we give it some time (30s)
        # to propagate in the cluster before returning.
        #
        # Returns a dict of <topic,future>.
        config = self.get_config()
        admin_clinet = AdminClient(config)
        fs = admin_clinet.delete_topics([topic], operation_timeout=30)

        # Wait for operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                logging.info("Topic {} deleted".format(topic))
            except Exception as e:
                logging.info("Failed to delete topic {}: {}".format(topic, e))

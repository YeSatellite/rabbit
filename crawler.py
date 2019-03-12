from threading import Thread
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

import pika
from pika.adapters.blocking_connection import BlockingChannel

host = pika.ConnectionParameters(host='localhost')

EXCHANGE_NAME = 'crawler'
QUEUE_NAME = 'worker'


class Crawler:
    def __init__(self, key):
        connection = pika.BlockingConnection(host)
        self.channel: BlockingChannel = connection.channel()

        self.channel.exchange_declare(exchange=EXCHANGE_NAME,
                                      exchange_type='direct')

        self.key = key

    def get(self, tasks):
        if isinstance(tasks, str):
            tasks = [tasks]

        for task in tasks:
            self.channel.basic_publish(exchange=EXCHANGE_NAME,
                                       routing_key=self.key,
                                       body=task)


class Worker:
    def __init__(self, key, callback):
        connection = pika.BlockingConnection(host)
        self.channel: BlockingChannel = connection.channel()

        self.channel.exchange_declare(exchange=EXCHANGE_NAME,
                                      exchange_type='direct')
        self.channel.queue_declare(queue=QUEUE_NAME)

        self.channel.queue_bind(exchange=EXCHANGE_NAME,
                                queue=QUEUE_NAME,
                                routing_key=key)

        def mq_callback(ch, method, properties, body):
            url = body.decode("utf-8")

            req = Request(url, headers={'User-Agent': "Magic Browser"})
            con = urlopen(req)

            soup = BeautifulSoup(con.read(), 'html.parser')
            for tag in soup.select('div.contentbox h2.style1 a'):
                callback(tag.getText().strip())

            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(consumer_callback=mq_callback,
                                   queue=QUEUE_NAME)

    def ready(self):
        thread = Thread(target=self.channel.start_consuming)
        thread.start()

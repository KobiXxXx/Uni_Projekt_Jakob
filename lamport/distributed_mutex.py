import paho.mqtt.client as mqtt
import json

class DistributedMutex:
    """
    Implementiert Lamport's Algorithmus zur gegenseitigen Ausschließung.
    """
    def __init__(self, worker_id, lamport_clock):
        self.worker_id = worker_id
        self.max_workers = 3
        self.lamport_clock = lamport_clock
        self.request_queue = []
        self.reply_count = 0
        self.requesting_cs = False
        
        # MQTT setup
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("mosquitto", 8883)
        
        self.client.subscribe("request")
        self.client.subscribe("reply")
        self.client.subscribe("release")
        self.client.loop_start()

    def request_cs(self):
        self.requesting_cs = True
        self.reply_count = 0
        ts = self.lamport_clock.increment()
        
        self.request_queue.append((ts, self.worker_id))
        self.request_queue.sort(key=lambda x: (x[0], x[1]))
        print(f"DISTRIBUTED MUTEX: Requesting CS at timestamp {ts}.")
        
        message = {
            "type": "request",
            "timestamp": ts,
            "worker_id": self.worker_id
        }
        self.client.publish("request", json.dumps(message))

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)

        # Skip messages from self
        if data["worker_id"] == self.worker_id:
            return
        
        if msg.topic == "request":
            ts = self.lamport_clock.update(data["timestamp"])
            self.request_queue.append((data["timestamp"], data["worker_id"]))
            self.request_queue.sort(key=lambda x: (x[0], x[1]))
        
            reply = {
                "type": "reply",
                "timestamp": self.lamport_clock.increment(),
                "worker_id": self.worker_id,
                "to_worker_id": data["worker_id"]
            }
            self.client.publish("reply", json.dumps(reply))

        elif msg.topic == "reply" and data["to_worker_id"] == self.worker_id:
            ts = self.lamport_clock.update(data["timestamp"])
            self.reply_count += 1
            print(f"DISTRIBUTED MUTEX: Received reply from Worker {data['worker_id']} at timestamp {ts}.")

        elif msg.topic == "release":
            ts = self.lamport_clock.update(data["timestamp"])
            print(f"DISTRIBUTED MUTEX: Received release from Worker {data['worker_id']} at timestamp {ts}.")
            self.request_queue = [(t, w) for t, w in self.request_queue if w != data["worker_id"]]
            self.request_queue.sort(key=lambda x: (x[0], x[1]))

    def can_enter_cs(self):
        if not self.requesting_cs:
            return False
        if self.reply_count < self.max_workers - 1:
            return False
        if not self.request_queue: 
            return False
        ts, worker = self.request_queue[0]
        can_enter = worker == self.worker_id
        if can_enter:
            print(f"DISTRIBUTED MUTEX: Entering CS at timestamp {self.lamport_clock.time}.")
        return can_enter

    def release_cs(self):
        self.requesting_cs = False
        ts = self.lamport_clock.increment()
        print(f"DISTRIBUTED MUTEX: Releasing CS at timestamp {ts}.")
        
        self.request_queue = [(t, w) for t, w in self.request_queue if w != self.worker_id]
        self.request_queue.sort(key=lambda x: (x[0], x[1]))

        message = {
            "type": "release",
            "timestamp": ts,
            "worker_id": self.worker_id
        }
        self.client.publish("release", json.dumps(message))
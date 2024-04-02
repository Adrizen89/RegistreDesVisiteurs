import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
from win11toast import toast
import socket

from winotify import Notification

hostname = socket.gethostname()

load_dotenv()
MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_TOPIC = f"{os.getenv('MQTT_TOPIC')}{hostname}"
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

def on_connect(client, userdata, flags, rc):
    print("Connecté avec succès")
    # S'abonner à un topic
    print(MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")
    Notification(app_id="Registre des Visiteurs", title="Un visiteur est là pour vous", msg=msg.payload.decode()).show()

# Création du client MQTT
client = mqtt.Client()

# Assignation des callbacks
client.on_connect = on_connect
client.on_message = on_message

client.tls_set()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Connexion au broker
client.connect(MQTT_SERVER, MQTT_PORT, 60)

# Boucle de traitement des messages
client.loop_forever()

from PyQt5 import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFormLayout,QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
from PyQt5.QtGui import QPixmap
from dotenv import load_dotenv
import sys
import os
import paho.mqtt.client as mqtt
import time

class VisitorForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registre des Visiteurs")
        self.setGeometry(100, 100, 900, 1000)
        load_dotenv()
        
        # Création des widgets
        
        self.logoLabel = QLabel(self)
        self.logoPixmap = QPixmap('./dad.jpg')
        self.logoLabel.setPixmap(self.logoPixmap)
        self.logoLabel.setScaledContents(True) 
        
        self.societeLabel = QLabel('Société / Compagny :')
        self.societeLineEdit = QLineEdit()
        
        self.nameLabel = QLabel('Nom du Visiteur:')
        self.nameLineEdit = QLineEdit()
        
        self.nbreVisiteursLabel = QLabel('Nombre de Visiteur(s) / Number of Visitor(s) :')
        self.nbreVisiteursComboBox = QComboBox()
        self.nbreVisiteursComboBox.addItems(['1', '2', '3', '4', '5', '+ 5'])
        
        self.objetLabel = QLabel('Objet de la visite / Reason for visit :')
        self.objetLineEdit = QLineEdit()

        self.employeeLabel = QLabel('Réunion avec / Meeting with :')
        self.employeeComboBox = QComboBox()
        self.employeeComboBox.addItems(["Adrien", "Theo", "Johan", "Nathan"])

        self.submitButton = QPushButton('Enregistrer')
        self.submitButton.clicked.connect(self.submitForm)
        
        # Mise en place du layout
        layout = QVBoxLayout()
        layout.addWidget(self.logoLabel) 
        layout.addWidget(self.societeLabel)
        layout.addWidget(self.societeLineEdit)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.nameLineEdit)
        layout.addWidget(self.nbreVisiteursLabel)
        layout.addWidget(self.nbreVisiteursComboBox)
        layout.addWidget(self.objetLabel)
        layout.addWidget(self.objetLineEdit)
        layout.addWidget(self.employeeLabel)
        layout.addWidget(self.employeeComboBox)
        layout.addWidget(self.submitButton)
        
        self.setLayout(layout)
        
    def submitForm(self):
        MQTT_SERVER = os.getenv('MQTT_SERVER')
        MQTT_PORT = int(os.getenv('MQTT_PORT'))
        MQTT_TOPIC = os.getenv('MQTT_TOPIC')
        MQTT_USER = os.getenv('MQTT_USER')
        MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

        client = mqtt.Client()

        if MQTT_USER and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

        client.tls_set()  # Si vous utilisez TLS
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_start()  # Démarre la boucle d'arrière-plan

        # Attendez que la connexion soit établie
        time.sleep(1.5)  # Un délai pour s'assurer que la connexion a eu le temps de s'établir

        # Publication d'un message
        info = client.publish(MQTT_TOPIC, "23°C")
        info.wait_for_publish()  # Attendre que la publication soit complétée

        client.loop_stop()  # Arrête la boucle d'arrière-plan
        client.disconnect()  # Se déconnecte proprement

        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Publication réussie")
        else:
            print("Échec de la publication")

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VisitorForm()
    ex.show()
    sys.exit(app.exec_())
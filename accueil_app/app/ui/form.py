from PyQt5 import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QTextEdit, QToolButton,QCheckBox,QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
from PyQt5.QtGui import QPixmap
from dotenv import load_dotenv
import sys
import os
import paho.mqtt.client as mqtt
import time
from ..core.api_client import APIClient

import socket

class ConditionsDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Conditions Générales")
        self.setGeometry(100, 100, 600, 400)  # Ajustez la taille selon le besoin
        
        layout = QVBoxLayout()
        
        self.conditionsText = QTextEdit()
        self.conditionsText.setReadOnly(True)  # Rendre le texte non éditable
        # Chargez votre texte ici, exemple :
        self.conditionsText.setText("Ici seront affichées les conditions générales...")
        
        layout.addWidget(self.conditionsText)
        
        self.setLayout(layout)


class VisitorForm(QWidget):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.initUI()
        
    def initUI(self):
        self.loadStyleSheet('./style.css')
        self.setWindowTitle("Registre des Visiteurs")
        self.setGeometry(100, 100, 900, 1000)
        load_dotenv()
        
        employe_topic = self.api_client.extract_name_topic()

        self.noms = [poste["nom"] for poste in employe_topic["postes"]]
        self.topics = {poste["nom"]: poste["topic"] for poste in employe_topic["postes"]}
        
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
        self.employeeComboBox.addItems(self.noms)
        
        self.afficherConditionsBtn = QToolButton()
        self.afficherConditionsBtn.setText('Afficher les conditions générales / Show the Generals Conditions')
        self.afficherConditionsBtn.clicked.connect(self.afficherConditions)
        
        self.checkConditions = QCheckBox("J'accepte les conditions générales d'utilisation / I have read and accept the Generals Conditions", self)
        self.checkConditions.stateChanged.connect(self.checkboxEtatChange)

        self.submitButton = QPushButton('Enregistrer')
        self.submitButton.clicked.connect(self.submitForm)
        self.submitButton.setEnabled(False)
        
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
        layout.addWidget(self.afficherConditionsBtn)
        layout.addWidget(self.checkConditions)
        layout.addWidget(self.submitButton)
        
        self.setLayout(layout)
    
    def afficherConditions(self):
        self.dialogueConditions = ConditionsDialog()
        self.dialogueConditions.show()
    
    def checkboxEtatChange(self, state):
        self.submitButton.setEnabled(state == Qt.Checked)
        if state == Qt.Checked:
            print("Checkbox cochée")
        else:
            print("Checkbox décochée")
            
    def loadStyleSheet(self, path):
        with open(path, "r") as fh:
            self.setStyleSheet(fh.read())
        
    def submitForm(self):
        
        employe = self.employeeComboBox.currentText()
        topic_selectionne = self.topics.get(employe, None)
        
        MQTT_SERVER = os.getenv('MQTT_SERVER')
        MQTT_PORT = int(os.getenv('MQTT_PORT'))
        MQTT_TOPIC = f"{os.getenv('MQTT_TOPIC')}{topic_selectionne}"
        MQTT_USER = os.getenv('MQTT_USER')
        MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
        
        arrivant = self.nameLineEdit.text()

        client = mqtt.Client()

        if MQTT_USER and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

        client.tls_set()
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_start()

        
        time.sleep(1.5)

        response = self.api_client.send_data_to_service(arrivant, employe)
        if response:
            print("Les données ont été envoyées avec succès !")
        else:
            print("Une erreur s'est produite lors de l'envoi des données !")
            
        # Publication d'un message
        info = client.publish(f"{MQTT_TOPIC}", f"{arrivant} est arrivé !")
        info.wait_for_publish()

        client.loop_stop()
        client.disconnect()

        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Publication réussie")
            print(f"Publication sur le topic : {MQTT_TOPIC}")

        else:
            print("Échec de la publication")

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VisitorForm()
    ex.show()
    sys.exit(app.exec_())
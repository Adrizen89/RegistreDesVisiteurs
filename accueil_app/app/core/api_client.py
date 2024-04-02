import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL_RECEIVE = os.getenv('URL_RECEIVE')
URL_EXTRACT = os.getenv('URL_EXTRACT')
BEARER_RECEIVE = os.getenv('BEARER_RECEIVE')
BEARER_EXTRACT = os.getenv('BEARER_EXTRACT')
TOPIC_RECEIVE = os.getenv('TOPIC_RECEIVE')
TOPIC_EXTRACT = os.getenv('TOPIC_EXTRACT')

class APIClient:
    def __init__(self, 
                 base_url_receive=URL_RECEIVE, 
                 base_url_extract=URL_EXTRACT,
                 ):
        self.base_url_receive = base_url_receive
        self.base_url_extract = base_url_extract

    def send_data_to_service(self, arrivant, employe, societe, nbreVisiteur, objet, conditions):
        full_url = f"{self.base_url_receive}{TOPIC_RECEIVE}"
        params = {"id1": arrivant, "id2": employe, "id3": societe, "id4": nbreVisiteur, "id5": objet, "id6": conditions }
        bearer_receive = BEARER_RECEIVE
        header = {'Authorization': f'Bearer {bearer_receive}'}
        response = requests.post(full_url, params=params, headers=header)

        return response
    
    def extract_name_topic(self):
        full_url_extract = f"{self.base_url_extract}{TOPIC_EXTRACT}"
        bearer_extract = BEARER_EXTRACT
        header_topic = {'Authorization':f'Bearer {bearer_extract}'}
        response = requests.get(full_url_extract, headers=header_topic )
        if response:
            employes = response.json()
            return employes
        else:
            print("Erreur pour l'extraction des données !")

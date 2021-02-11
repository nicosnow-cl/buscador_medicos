import requests
import time 

class APISuperDeSalud:
    def __init__(self, rut):
        self.rut_medico = rut
        self.base_url = 'https://apis.superdesalud.gob.cl/api/prestadores/rut/'
        self.auth_key = '?apikey=6D8B4E2hrAdwnPK4yHt623NbDnXhTOlC'
        self.type_file = '.json/'

    def normalizeRut(self):
        self.rut_medico = self.rut_medico.replace('.', '')
        self.rut_medico = self.rut_medico.replace('-', '')
        self.rut_medico = self.rut_medico[:-1]

    def getAntecedentes(self):
        self.normalizeRut()
        request_url = self.base_url + self.rut_medico + self.type_file + self.auth_key
        response = requests.get(request_url, timeout = 5)
        time.sleep(1)
        if response.status_code == 200: return response.json()
        return False
        
class APISuperDeSalud:
    def __init__(self, rut):
        import urllib.request as request
        import json

        self.rut = rut
        self.auth_key = 'X6tzL8HGhWxeOalCNrXt4sXHaHSgmzdqGhKo8prG'
        self.request = request
        self.json = json
        self.data = None

    def run(self):
        self.rut = self.rut.replace('.', '')
        self.rut = self.rut.replace('-', '')
        self.rut = self.rut[:-1]

        url = 'https://api.superdesalud.gob.cl/prestadores/v1/prestadores/antecedentes/'+self.rut+'.json/?auth_key='+self.auth_key
        response = self.request.urlopen(url).read()
        self.data = self.json.loads(response.decode('utf-8'))

        return self.data
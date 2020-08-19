class ScraperTransparencia:
    def __init__(self, hospital, comuna, outputs=False):
        import unicodedata as unicode
        import urllib.request as request
        import urllib.parse as parse
        from bs4 import BeautifulSoup
        import random
        import time
        import pandas as pd

        self.hospital = hospital
        self.comuna = comuna
        self.outputs=outputs
        self.months = []
        self.years = []
        self.tipos = ['contrata', 'planta']
        self.unicode = unicode
        self.request = request
        self.parse = parse
        self.bs4 = BeautifulSoup
        self.pd = pd
        self.random = random
        self.time = time
        self.df_medicos = None
        self.planta_contrata_links = dict()
        self.date_remunerations_dict = dict()
        self.encontrado = False

    def getPlantaAndContrataURLs(self):
        print('\nObteniendo URLs de Planta y Contrata para ' + str(self.hospital)) if self.outputs else None

        intentos = 0
        while intentos < 3:
            try:
                hosp_comuna = self.parse.quote(self.hospital + ', ' + self.comuna)
                url = 'https://www.portaltransparencia.cl/PortalPdT/web/guest/home?p_p_id=3&p_p_lifecycle=0&p_p_state=maximized&p_p_mode=view&_3_struts_action=/search/search&_3_redirect=/PortalPdT/web/guest/home?p_auth=gVKA8DxS&p_p_id=3&p_p_lifecycle=1&p_p_state=normal&p_p_state_rcv=1&_3_groupId=0&x=0&y=0&_3_keywords=' + hosp_comuna + '&search_term=' + hosp_comuna
                page_1 = self.request.urlopen(url).read().decode('utf-8')
                self.time.sleep(0.2)

                soup = self.bs4(page_1, 'html.parser')
                key = self.hospital.lower()
                tag = soup.find(lambda tag: tag.name == 'a' and key in tag.text.lower())
                link_1 = tag.get('href')

                url = link_1
                page_2 = self.request.urlopen(url).read().decode('utf-8')
                self.time.sleep(0.2)

                soup = self.bs4(page_2, 'html.parser')
                tag = soup.find('div', {'class': 'enlace_ficha_org'}).find('a', {'class': 'estilo_info_ta'})
                href = tag.get('href')
                url, sep, cod = href.partition('=')
                link_2 = url

                if cod != '':
                    url = link_2 + '=' + cod
                    page_3 = self.request.urlopen(url).read().decode('utf-8')
                    self.time.sleep(0.5)

                    soup = self.bs4(page_3, 'html.parser')
                    tag_1 = soup.find('a', attrs={'title': lambda x: x and x.lower() == 'personal a contrata'})
                    tag_2 = soup.find('a', attrs={'title': lambda x: x and x.lower() == 'personal de planta'})
                    self.planta_contrata_links[self.hospital] = [tag_1.get('href'), tag_2.get('href')]
                    intentos = 3
                    print('Completado.') if self.outputs else None

                else:
                    intentos = 3
                    print('La página de este hospital no pertenece a Transparencia.') if self.outputs else None
            except Exception as e:
                if intentos < 2:
                    print('En el intento %s se produjo un error.' % str(intentos + 1)) if self.outputs else None
                    intentos = intentos + 1
                else:
                    print('Se excedio el limite de intentos para este hospital.') if self.outputs else None
                    intentos = intentos + 1

    def getRemuneracionesByDate(self):
        from urllib.error import HTTPError

        def recursive(href, i, keys, depth=3):
            if depth != 0:
                j = 0

                while j < 3:
                    try:
                        page = self.request.urlopen(href).read().decode('utf-8')
                        self.time.sleep(0.5)
                    except HTTPError as e:
                        print('Ocurrio un error al alcanzar la URL | Error: ' + str(e.code))
                        print('Reintentando...')
                        j = j + 1
                    else:
                        j = 3
                        soup = self.bs4(page, 'html.parser')

                        if soup.find('table'):
                            tag_ = soup.find('table')

                            if i == 0:
                                dfs.append(self.pd.read_html(str(tag_))[0])
                            else:
                                dfs.append(self.pd.read_html(str(tag_))[0])
                        else:
                            for key in keys:
                                if soup.find(lambda tag: tag.name == 'a' and key.lower() in tag.text.lower()):
                                    tag = soup.find(lambda tag: tag.name == 'a' and key.lower() in tag.text.lower())
                                    url = tag.get('href')
                                    keys.remove(key)
                                    recursive(url, i, keys, depth - 1)

        dfs = list()

        for i, url in enumerate(self.planta_contrata_links[self.hospital]):
            print('Buscando en: ' + url) if self.outputs else None
            keys = [self.years[0], self.months[0], 'medica', 'médica']
            j = 0

            while j < 3:
                try:
                    page = self.request.urlopen(url).read().decode('latin-1')
                    self.time.sleep(0.5)
                except HTTPError as e:
                    print('Ocurrio un error al alcanzar la URL inicial | Error code: ' + str(e.code)) if self.outputs else None
                    print('Reintentando...') if self.outputs else None
                    j += 1
                else:
                    j = 3
                    soup = self.bs4(page, 'html.parser')

                    for key in keys:
                        if soup.find(lambda tag: tag.name == 'a' and key in tag.text.lower()):
                            tag = soup.find(lambda tag: tag.name == 'a' and key in tag.text.lower())
                            href = tag.get('href')

                            if url != None:
                                break

                    recursive(href, i, keys, 5)

            if len(dfs) <= i:
                print('El formato no coincide: puede que no hayan registros para esta fecha, la tabla se encuentra en formato PDF u ocurrio un error HTTP.') if self.outputs else None
                dfs.append(self.pd.DataFrame())
            else:
                print('Resultado: Se ha encontrado una tabla y se han rescatado los datos.') if self.outputs else None

        return dfs

    def createMedicosDict(self, dfs):
        df_medicos = self.pd.concat(dfs)
        df_medicos.columns = df_medicos.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df_medicos.columns = map(str.upper, df_medicos.columns)
        df_medicos = df_medicos.apply(lambda x: x.astype(str).str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))
        df_medicos = df_medicos[df_medicos['ESTAMENTO'].str.contains('MEDICO')]
        df_medicos = df_medicos.loc[:, ['NOMBRE COMPLETO', 'CARGO O FUNCION', 'GRADO EUS / CARGO CON JORNADA', 'CALIFICACION PROFESIONAL O FORMACION']]
        df_medicos = df_medicos.rename(columns={'NOMBRE COMPLETO':'NOMBRE', 'CARGO O FUNCION':'CARGO', 'GRADO EUS / CARGO CON JORNADA':'GRADO', 'CALIFICACION PROFESIONAL O FORMACION':'CALIFICACION'})
        idx_range = list(range(len(df_medicos)))
        df_medicos['ID'] = idx_range
        df_medicos = df_medicos.set_index('ID')
        return df_medicos.to_dict(orient='index')

    def run(self):
        from datetime import date, timedelta
        import locale
        locale.setlocale(locale.LC_ALL, 'spanish')
        medicos_dict = None

        print('### INICIANDO SCRAPING ###')

        last_month = date.today().replace(day=1) - timedelta(60)
        self.years.append(str(last_month.strftime("%Y")))
        self.months.append(str(last_month.strftime("%B")).capitalize())

        self.hospital = self.hospital.replace('Dr.', '')
        self.hospital = self.hospital.replace('Psiquiátrico', '')
        self.hospital = " ".join(self.hospital.split())

        self.getPlantaAndContrataURLs()

        if len(self.planta_contrata_links) > 0:
            print('\nLa lista de URLs obtenidas es: ' + str(self.planta_contrata_links)) if self.outputs else None
            dfs = self.getRemuneracionesByDate()
            medicos_dict = self.createMedicosDict(dfs)

            if len(medicos_dict) > 0:
                self.encontrado = True

        return self.encontrado, medicos_dict
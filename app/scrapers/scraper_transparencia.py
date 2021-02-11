from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs4
from itertools import combinations 
import urllib.parse as parse
import urllib.request as request
import pandas as pd
import time
import datetime
import locale

class ScraperTransparencia:
    def __init__(self, nombre_hospital, nombre_comuna, outputs=False):
        self.nombre_hospital = nombre_hospital
        self.nombre_comuna = nombre_comuna
        self.outputs = outputs
        self.months = [
            'dic', 'nov', 'oct', 
            'sep', 'ago', 'jul', 
            'jun', 'may', 'abr', 
            'mar', 'feb', 'ene'
            ]
        self.years = []
        self.tipos = [
            'personal de planta', 'personal a contrata'
            ] # Tipos de funcionarios de Portal de Transparencia de los cuales rescataremos sus datos     
        self.planta_contrata_links = dict()
        self.date_remunerations_dict = dict()
        self.encontrado = False
        self.chrome_driver = None
        self.df_medicos = []
        self.dict_medicos = {}

    def createMedicosDict(self):
        df_medicos = self.df_medicos
        df_medicos.columns = df_medicos.columns.str.normalize('NFKD').str.encode('ascii', errors = 'ignore').str.decode('utf-8')
        df_medicos.columns = map(str.upper, df_medicos.columns)
        df_medicos = df_medicos.apply(lambda x: x.astype(str).str.upper().str.normalize('NFKD').str.encode('ascii', errors = 'ignore').str.decode('utf-8'))        
        df_medicos = df_medicos[df_medicos['ESTAMENTO'].str.contains('MEDICO')]
        df_medicos = df_medicos.loc[:, ['NOMBRE COMPLETO', 'TIPO', 'CARGO O FUNCION', 'ESTAMENTO', 'REMUNERACION BRUTA MENSUALIZADA']]
        df_medicos = df_medicos.rename(columns={'NOMBRE COMPLETO':'NOMBRE', 'TIPO':'TIPO', 'CARGO O FUNCION':'CARGO', 'ESTAMENTO':'ESTAMENTO', 'REMUNERACION BRUTA MENSUALIZADA':'REMUNERACION'})        
        idx_range = list(range(len(df_medicos)))
        df_medicos['ID'] = idx_range
        df_medicos = df_medicos.set_index('ID')
        self.dict_medicos = df_medicos.to_dict(orient='index')

    def htmlTableToDF(self, tipo_funcionario):
        try:
            span_navigator = self.chrome_driver.find_elements_by_xpath('//span[@class = "ui-paginator-pages"]/a')                 
            print('!!! Se ha encontrado la tabla de funcionarios: %s.' % tipo_funcionario) if self.outputs else None
            # total_pages = len(span_navigator) // 2 if len(span_navigator) > 2 else 1 # Calculamos el total de páginas de la tabla       
            total_pages = 1 # Valor de prueba
            total_dfs = []                                            
            for page in range(1, total_pages + 1):
                self.chrome_driver.find_element_by_xpath('//a[contains(@class, "ui-paginator-page") and contains(text(), "' + str(page) + '")]').click()
                time.sleep(1.5)
                html = self.chrome_driver.find_element_by_xpath('//div[contains(@class, "ui-datatable-tablewrapper")]').get_attribute('innerHTML')
                soup = bs4(html, 'html.parser')
                total_dfs.append(pd.concat(pd.read_html(str(soup))))            
            full_df = pd.concat(total_dfs)
            full_df['TIPO'] = tipo_funcionario.upper()
            full_df['Remuneración bruta mensualizada'] = full_df['Remuneración bruta mensualizada'].str.replace('.', '').astype(int)
            full_df = full_df.sort_values(['Cargo o función', 'Remuneración bruta mensualizada', 'Nombre completo'], ascending = (True, True, True))
            self.df_medicos.append(full_df)
        except NoSuchElementException: print('En la URL final no se pudo encontrar el "span de navegación" o la tabla de funcionarios.')                           

    def startChromeDriver(self):        
        options = webdriver.ChromeOptions() # Variable de configuración del chrome_driver
        # options.add_argument('headless') # Deshabilitamos la ventana de Google Chrome
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")            
        # Instanciamos el objeto WebDriver y accedemos a la url        
        self.chrome_driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) # Con .install() verificamos e instalamos la ultiva versión del navegador

    def stopChromeDriver(self):
        try:
            self.chrome_driver.close()
            self.chrome_driver.quit()
        except: print('No hay ningun navegador abierto.') if self.outputs else None

    def transformDictToList(self, meds_dict):
        med_list = []
        for id, data in meds_dict.items(): 
            data['ID'] = id + 1
            data['ACCIÓN'] = ''
            med_list.append(data) 
        return med_list

    def getContrataPlantaTables(self):
        """
            Paso 1: Obtener URLs de funcionarios de Planta y Contrata.
        """
        print('\nObteniendo URLs de Planta y Contrata para ' + str(self.nombre_hospital)) if self.outputs else None
        intentos = 0
        while intentos < 1:
            # Cargamos una consulta para el hospital actual en el PortalTransparencia
            hosp_comuna = parse.quote(self.nombre_hospital + ', ' + self.nombre_comuna)
            url = 'https://www.portaltransparencia.cl/PortalPdT/web/guest/home?p_p_id=3&p_p_lifecycle=0&p_p_state=maximized&p_p_mode=view&_3_struts_action=/search/search&_3_redirect=/PortalPdT/web/guest/home?p_auth=gVKA8DxS&p_p_id=3&p_p_lifecycle=1&p_p_state=normal&p_p_state_rcv=1&_3_groupId=0&x=0&y=0&_3_keywords=' + hosp_comuna + '&search_term=' + hosp_comuna
            results_search_page = request.urlopen(url).read().decode('utf-8')
            time.sleep(1)
            # Analizamos esta primera pagina en busca del enlace a la página del portal
            soup = bs4(results_search_page, 'html.parser')            
            lower_hospital_name = self.nombre_hospital.lower()
            words_in_hospital_name = combinations(lower_hospital_name.split(' '), 3)  
            possible_names = [' '.join(string) for string in words_in_hospital_name]
            tag = False
            for hospital_name in possible_names:
                tag = soup.find(lambda tag: tag.name == 'a' and hospital_name in tag.text.lower())
                if tag: break         
            if tag: # Si encontramos el portal de este hospital, comenzamos la busqueda
                url = tag.get('href')            
                # Inicializamos el chrome_driver de Selenium
                self.startChromeDriver()           
                # Para cada uno de los tipos de funcionarios buscaremos sus tablas de remuneraciones
                for tipo_funcionario in self.tipos:
                    table_found = False
                    self.chrome_driver.get(url)
                    time.sleep(2)                    
                    funcionarios_link = self.chrome_driver.find_element_by_xpath('//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "' + tipo_funcionario + '")]')
                    funcionarios_link.send_keys('\n')                                      
                    # Ahora intentaremos encontrar registros de los ultimos 3 años.
                    for year in self.years:
                        if table_found: break # Si encontramos la tabla de remuneraciones, salimos del ciclo actual                            
                        else:
                            try:
                                time.sleep(1)                            
                                year_link = self.chrome_driver.find_element_by_xpath('//a[@class = "ui-commandlink ui-widget tab-link" and contains(text(), "' + year + '")]')                            
                                year_link.send_keys('\n')
                                print('!!! Se ha encontrado un registro para el año de %s.' % year) if self.outputs else None
                                # Por cada año intentaremos encontrar los datos del mes mas reciente
                                for month in self.months:
                                    if table_found: break  # Si encontramos la tabla de remuneraciones, salimos del ciclo actual                                        
                                    else:
                                        try:
                                            time.sleep(1) 
                                            # month_link = self.chrome_driver.find_element_by_xpath('//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "' + month + '")]')
                                            month_link = self.chrome_driver.find_element_by_xpath('//a[@class = "ui-commandlink ui-widget tab-link" and contains(translate(text(), \
                                                                                                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "' + month + '")]')
                                            month_link.send_keys('\n')
                                            print('!!! Se ha encontrado un registro para el mes %s.' % month) if self.outputs else None                                                                                   
                                            try:
                                                time.sleep(2) 
                                                # Primero intentamos buscar el div que contiene la tabla, si es que existe
                                                self.chrome_driver.find_element_by_xpath('//div[@class = "ui-datatable-tablewrapper"]')                                            
                                                self.htmlTableToDF(tipo_funcionario)
                                                table_found = True
                                                intentos = 1
                                            except:
                                                # En caso de que no exista, probamos haciendo click en el elemento 'a' que contiene el texto 'ley medica'
                                                # Y luego buscamos el div que contiene la tabla, si es que existe
                                                try:
                                                    table_link = self.chrome_driver.find_element_by_xpath('//a[@class = "ui-commandlink ui-widget tab-link" and \
                                                                                                          contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "ley medica") or \
                                                                                                          contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸŽŠŒ", "abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿžšœ"), "ley médica")]')
                                                    table_link.send_keys('\n')
                                                    time.sleep(2)
                                                    self.htmlTableToDF(tipo_funcionario)                                     
                                                    table_found = True
                                                    intentos = 1
                                                except NoSuchElementException: print('No se pudo encontrar la tabla de funcionarios.') if self.outputs else None                                            
                                        except NoSuchElementException: print('No existen registros para el mes %s.' % month) if self.outputs else None
                            except NoSuchElementException: print('No existen registros para el año %s.' % year) if self.outputs else None          
                intentos += 1           
            else:
                intentos = 1
                print('No se ha podido encontrar el portal de este organismo.')
        self.stopChromeDriver()
    
    def normalizeHospitalName(self):
        self.nombre_hospital = self.nombre_hospital.replace('Dr.', '')
        self.nombre_hospital = self.nombre_hospital.replace('Doctor', '')
        self.nombre_hospital = self.nombre_hospital.replace('Psiquiátrico', '')
        self.nombre_hospital = self.nombre_hospital.replace('Regional', '')
        self.nombre_hospital = " ".join(self.nombre_hospital.split())

    def run(self):        
        locale.setlocale(locale.LC_ALL, 'spanish')
        # Una pequeña modificación al nombre del hospital para mejorar la busqueda
        print(self.nombre_hospital)
        self.normalizeHospitalName()
        print(self.nombre_hospital)
        print('\n### INICIANDO SCRAPER DE PORTALTRANSPARENCIA ###')
        now = datetime.datetime.now()
        for i in range(0,2): self.years.append(str(now.year - i))
        # Obtenemos los dfs de medicos
        self.getContrataPlantaTables()
        self.df_medicos = pd.concat(self.df_medicos)
        # Modificamos los dfs para dejar solo los campos que nos interesan
        self.createMedicosDict()
        if len(self.dict_medicos) > 0: self.encontrado = True
        return self.encontrado, self.dict_medicos
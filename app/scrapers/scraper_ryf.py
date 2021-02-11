from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

class ScraperRyF:
    def __init__(self, nombre, outputs = False):
        self.nombre_medico = nombre
        self.outputs = outputs
        self.chrome_driver = None    
        self.encontrado = False
        self.rut = None 
        self.base_url = 'https://www.nombrerutyfirma.com/'      
    
    def startChromeDriver(self):        
        options = webdriver.ChromeOptions() # Variable de configuración del chrome_driver
        # options.add_argument('headless') # Deshabilitamos la ventana de Google Chrome
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")            
        # Instanciamos el objeto WebDriver y accedemos a la url        
        self.chrome_driver = webdriver.Chrome(ChromeDriverManager().install(), options = options) # Con .install() verificamos e instalamos la ultiva versión del navegador

    def stopChromeDriver(self):
        self.chrome_driver.close()
        self.chrome_driver.quit()

    def searchByName(self):
        try:
            input_search = self.chrome_driver.find_element_by_name('term')
            input_search.send_keys(self.nombre_medico)
            input_search.submit()        
            try:            
                time.sleep(2)
                # html_table = self.chrome_driver.find_element_by_tag_name('table').get_attribute('outerHTML')
                html_table = self.chrome_driver.find_element_by_xpath('//table[@class = "table table-hover"]').get_attribute('outerHTML')
                print('Se ha encontrado la tabla de personas.') if self.outputs else None
                df_personas = pd.read_html(html_table)[0]
                if df_personas.shape[0] > 0:
                    try:
                        print('Transformando datos.')                        
                        splitted_name = self.nombre_medico.split(' ')
                        # medico_encontrado = df_personas[df_personas['Nombre'].str.contains('|'.join(splitted_name))].head(1)
                        # self.rut = medico_encontrado['RUT'][0]
                        self.rut = df_personas[df_personas['Nombre'].str.contains('|'.join(splitted_name))]['RUT'][0]
                        self.encontrado = True
                    except: print('Ocurrio un problema al normalizar los datos de la tabla.') if self.outputs else None
                else: print('No existen registros para este nombre.') if self.outputs else None
            except: print('No se pudo encontrar la tabla de personas.') if self.outputs else None
        except NoSuchElementException: print('No se encontro ningún campo de input dentro de la página.') if self.outputs else None

    def getRut(self):
        print('### INICIANDO SCRAPER NOMBRE, RUT Y FIRMA ###') if self.outputs else None
        print('\nObteniendo RUT del médico ' + str(self.nombre_medico)) if self.outputs else None
        self.nombre_medico = self.nombre_medico.replace(',', '').title()
        self.startChromeDriver()
        self.chrome_driver.get(self.base_url)
        time.sleep(2)
        self.searchByName()
        self.stopChromeDriver()
        if self.encontrado: print('El Scraper ha encontrado el siguiente RUT %s para el medico %s.' % (self.rut, self.nombre_medico)) if self.outputs else None
        else: print('El Scraper no fue capaz de encontrar ningún RUT para el medico %s.' % self.nombre_medico) if self.outputs else None
        return self.encontrado, self.rut
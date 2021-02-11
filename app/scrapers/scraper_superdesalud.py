from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

class ScraperSuperDeSalud:
    def __init__(self, nombre, outputs = False):
        self.nombre_medico = nombre
        self.outputs = outputs
        self.base_url = 'https://rnpi.superdesalud.gob.cl/'
        self.chrome_driver = None        
    
    def startChromeDriver(self):        
        options = webdriver.ChromeOptions() # Variable de configuración del chrome_driver
        # options.add_argument('headless') # Deshabilitamos la ventana de Google Chrome
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")            
        # Instanciamos el objeto WebDriver y accedemos a la url        
        self.chrome_driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) # Con .install() verificamos e instalamos la ultiva versión del navegador

    def stopChromeDriver(self):
        self.chrome_driver.close()
        self.chrome_driver.quit()
    
    def getRutMedico(self):
        print('Ingresando a url de SuperIntendencia de Salud.')
        self.startChromeDriver()
        self.chrome_driver.get(self.base_url)
        time.sleep(3)
        form_element = self.chrome_driver.find_element_by_xpath('//form[@class = "form-inline center col-12 my-2 my-lg-0 ng-valid ng-dirty ng-valid-parse ng-touched ng-not-empty ng-pristine"]')
        input_element = self.chrome_driver.find_element_by_xpath('//input[@type = "text"]')
        input_element.send_keys(self.nombre_medico)
        input_element.send_keys(Keys.RETURN)
        time.sleep(3)
        return False, '111111111'


class ScraperRYF:
    def __init__(self, nombre, outputs=False):
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        import pandas as pd
        import time

        self.nombre = nombre
        self.outputs = outputs
        self.webdriver = webdriver
        self.chrome_driver_manager = ChromeDriverManager
        self.pd = pd
        self.time = time
        self.rut = None
        self.encontrado = False

    def seleniumDriver(self, url):
        # Deshabilitar la ventana de Google Chrome de WebDriver
        options = self.webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        # Instanciamos el objeto WebDriver y accedemos a la url
        # Con ChromeDriverManager() instalamos la ultima versión compatible del webdriver de Chrome a través del repositorio oficial
        chrome_driver = self.webdriver.Chrome(self.chrome_driver_manager().install(), options=options)
        chrome_driver.get(url)

        input = chrome_driver.find_element_by_name('term')
        input.send_keys(self.nombre)
        input.submit()

        self.time.sleep(1)

        table = chrome_driver.find_element_by_tag_name('table').get_attribute("outerHTML")
        df_personas = self.pd.read_html(table)[0]
        chrome_driver.quit()

        if len(df_personas) > 0:
            parsed_name = self.nombre.replace(',', '').upper()
            df_personas = df_personas.apply(lambda x: x.astype(str).str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))
            medico = df_personas[df_personas['Nombre'] == parsed_name].head(1)
            self.rut = medico['RUT'][0]
            self.encontrado = True

    def getRUT(self):
        print('\nObteniendo RUT del médico ' + str(self.nombre)) if self.outputs else None

        try:
            url = 'https://www.nombrerutyfirma.com/'
            self.seleniumDriver(url)
        except Exception as e:
            print(e)

    def run(self):
        print('### INICIANDO SCRAPING ###')
        self.getRUT()
        return self.encontrado, self.rut
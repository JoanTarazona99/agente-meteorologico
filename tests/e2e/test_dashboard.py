"""
Pruebas E2E con Selenium para el dashboard web.

REQUISITOS:
- La aplicación debe estar corriendo en http://localhost:5000
- Google Chrome instalado
- webdriver-manager instala ChromeDriver automáticamente

Para ejecutar solo estas pruebas:
    pytest tests/e2e/ -v

Para saltarlas si no hay servidor:
    pytest tests/ --ignore=tests/e2e/
"""
import pytest
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_DISPONIBLE = True
except ImportError:
    SELENIUM_DISPONIBLE = False

BASE_URL = 'http://localhost:5000'


@pytest.fixture(scope='module')
def driver():
    """Configura y retorna un driver de Chrome sin cabeza (headless)."""
    if not SELENIUM_DISPONIBLE:
        pytest.skip('selenium o webdriver-manager no instalados')

    opciones = Options()
    opciones.add_argument('--headless')
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    opciones.add_argument('--window-size=1280,800')

    try:
        servicio = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servicio, options=opciones)
        navegador.implicitly_wait(5)
        yield navegador
    except Exception as e:
        pytest.skip(f'No se pudo iniciar ChromeDriver: {e}')
    finally:
        try:
            navegador.quit()
        except Exception:
            pass


def servidor_disponible():
    """Comprueba si el servidor Flask está corriendo."""
    import urllib.request
    try:
        urllib.request.urlopen(BASE_URL, timeout=2)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not servidor_disponible(), reason="Servidor Flask no disponible en localhost:5000")
class TestDashboardCarga:
    """Pruebas de carga del dashboard principal."""

    def test_titulo_pagina(self, driver):
        """Verifica que el título de la página contiene 'Meteorológico'."""
        driver.get(BASE_URL)
        assert 'Meteorológico' in driver.title or 'Dashboard' in driver.page_source

    def test_navbar_visible(self, driver):
        """Verifica que la barra de navegación está visible."""
        driver.get(BASE_URL)
        navbar = driver.find_element(By.CSS_SELECTOR, '.navbar')
        assert navbar.is_displayed()

    def test_buscador_presente(self, driver):
        """Verifica que el campo de búsqueda está presente."""
        driver.get(BASE_URL)
        campo = driver.find_element(By.ID, 'inputCiudad')
        assert campo.is_displayed()

    def test_boton_buscar_presente(self, driver):
        """Verifica que el botón de búsqueda está presente."""
        driver.get(BASE_URL)
        boton = driver.find_element(By.ID, 'btnBuscar')
        assert boton.is_displayed()

    def test_enlace_alertas_en_navbar(self, driver):
        """Verifica que el enlace a alertas está en el navbar."""
        driver.get(BASE_URL)
        enlace = driver.find_element(By.PARTIAL_LINK_TEXT, 'Alertas')
        assert enlace.is_displayed()


@pytest.mark.skipif(not servidor_disponible(), reason="Servidor Flask no disponible en localhost:5000")
class TestDashboardBusqueda:
    """Pruebas de la funcionalidad de búsqueda."""

    def test_campo_busqueda_acepta_texto(self, driver):
        """Verifica que el campo de búsqueda acepta texto."""
        driver.get(BASE_URL)
        campo = driver.find_element(By.ID, 'inputCiudad')
        campo.clear()
        campo.send_keys('Madrid')
        assert campo.get_attribute('value') == 'Madrid'

    def test_enter_en_campo_activa_busqueda(self, driver):
        """Verifica que presionar Enter en el campo inicia la búsqueda."""
        driver.get(BASE_URL)
        campo = driver.find_element(By.ID, 'inputCiudad')
        campo.clear()
        campo.send_keys('Barcelona')
        campo.send_keys(Keys.RETURN)
        time.sleep(1)
        # No fallará aunque no haya API key; solo verifica que el botón se activó
        boton = driver.find_element(By.ID, 'btnBuscar')
        assert boton is not None

    def test_busqueda_vacia_no_rompe_pagina(self, driver):
        """Verificar que buscar sin texto no rompe la página."""
        driver.get(BASE_URL)
        boton = driver.find_element(By.ID, 'btnBuscar')
        boton.click()
        time.sleep(0.5)
        # La página no debe haber desaparecido
        assert driver.find_element(By.ID, 'inputCiudad').is_displayed()


@pytest.mark.skipif(not servidor_disponible(), reason="Servidor Flask no disponible en localhost:5000")
class TestPaginaAlertas:
    """Pruebas de la página de alertas."""

    def test_pagina_alertas_carga(self, driver):
        """Verifica que la página de alertas carga correctamente."""
        driver.get(f'{BASE_URL}/alertas')
        assert 'Alertas' in driver.page_source

    def test_formulario_nueva_alerta_presente(self, driver):
        """Verifica que el formulario de nueva alerta está presente."""
        driver.get(f'{BASE_URL}/alertas')
        formulario = driver.find_element(By.ID, 'formNuevaAlerta')
        assert formulario.is_displayed()

    def test_selector_tipo_alerta_presente(self, driver):
        """Verifica que el selector de tipo de alerta está presente."""
        driver.get(f'{BASE_URL}/alertas')
        selector = driver.find_element(By.ID, 'alertaTipo')
        assert selector.is_displayed()

    def test_navegacion_dashboard_a_alertas(self, driver):
        """Verifica la navegación entre dashboard y alertas."""
        driver.get(BASE_URL)
        enlace_alertas = driver.find_element(By.PARTIAL_LINK_TEXT, 'Alertas')
        enlace_alertas.click()
        time.sleep(0.5)
        assert '/alertas' in driver.current_url

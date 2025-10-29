import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import allure
import os

@pytest.fixture(scope="function")
def browser():
    """
    Фикстура для инициализации и закрытия браузера
    """
    # Настройки Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Устанавливаем неявное ожидание
    driver.implicitly_wait(10)
    
    # Передаем драйвер в тест
    yield driver
    
    # Закрываем браузер после теста
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для создания отчетов Allure
    """
    outcome = yield
    report = outcome.get_result()
    
    # Если тест упал, делаем скриншот
    if report.when == "call" and report.failed:
        try:
            # Получаем браузер из фикстуры
            browser = item.funcargs['browser']
            
            # Создаем скриншот
            screenshot = browser.get_screenshot_as_png()
            
            # Прикрепляем скриншот к отчету Allure
            allure.attach(
                screenshot,
                name="screenshot_on_failure",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Также сохраняем HTML страницу
            page_source = browser.page_source
            allure.attach(
                page_source,
                name="page_source_on_failure", 
                attachment_type=allure.attachment_type.HTML
            )
        except Exception as e:
            print(f"Failed to take screenshot on failure: {e}")

def pytest_configure(config):
    """
    Конфигурация pytest
    """
    # Создаем папку для результатов Allure если ее нет
    if not os.path.exists("allure-results"):
        os.makedirs("allure-results")

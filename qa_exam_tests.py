import time
import pytest
import random
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options)


class TestUI:
    url = "http://127.0.0.1:5000/"

    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(5)

    @allure.title("Заглавная страница")
    @allure.description(
        "проверить корректность расчета стоимости серверов. Формула расчета price = cpu**2 + ram*2 + ssd/4")
    def test_prices(self):
        cards_header = driver.find_elements(By.CSS_SELECTOR, "#Price .card-header")
        cards_text = driver.find_elements(By.CSS_SELECTOR, "#Price .card-text")
        cards_btn = driver.find_elements(By.CSS_SELECTOR, "#Price .btn")
        # Функция для рассчета стоимости
        calc = lambda cpu, ram, ssd: cpu ** 2 + ram * 2 + ssd / 4
        data = {}

        def cards_data(headers, texts, btns):
            """
            Собирает в словарь data необходимые данные с карточек на странице
            :param headers:
            :param texts:
            :param btns:
            :return:
            """
            for i in range(len(headers)):
                split_text = texts[i].text.split("\n")
                data[headers[i].text] = split_text, btns[i].text.split(" ")[2]

        cards_data(cards_header, cards_text, cards_btn)

        for i in data:
            cpu = int(data[i][0][0].split(" ")[0])
            ram = int(data[i][0][1].split(" ")[0])
            ssd = int(data[i][0][2].split(" ")[0])
            price = int(data[i][1].split("$")[1])
            with allure.step(f"Сравнивает корректность рассчета с текущим значением в карточке {i}"):
                assert calc(cpu, ram, ssd) == price

    @allure.title("Страница регистрации")
    @allure.description("1. проверить регистрацию по парам имя/пароль, email/пустой пароль, не корректный "
                        "email/пароль. проверить ответ по тексту уведомления об ошибке."
                        "2. проверить регистрацию по паре email/пароль"
                        "3. попробовать повторно авторизоваться с тем же значением email/пароль, проверить ответ по "
                        "тексту уведомления об ошибке")
    @pytest.mark.parametrize("email, password",
                             [("mb11@qa.qa", "   "), ("InvalidEmail", "qwerty"), ("mb11@qa.qa", "qwerty"),
                              (f"mb{random.randint(1, 99)}@qa.qa", "qwerty")])
    def test_register(self, email, password):
        #Переход на страницу регистрации
        register_btn = driver.find_element(By.LINK_TEXT, "Signup")
        register_btn.click()

        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        register_form_btn = driver.find_element(By.CSS_SELECTOR, "#registration-form .btn")

        #Отправка тестовых данных
        email_field.send_keys(email)
        pass_field.send_keys(password)
        register_form_btn.click()

        if email == "mb11@qa.qa" and password == "   ":
            with allure.step("Проверить email/пустой пароль"):
                alert = driver.find_element(By.CSS_SELECTOR, ".alert")
                assert alert.text == "Input payload validation failed"
        elif email == "InvalidEmail" and password == "qwerty":
            with allure.step("Проверить не корректный email/пароль"):
                alert = driver.find_element(By.CSS_SELECTOR, ".alert")
                assert alert.text == "Input payload validation failed"
        elif email == "mb11@qa.qa" and password == "qwerty":
            # На первый запуск упадет
            with allure.step("Проверить корректный, существующий имя/пароль"):
                alert = driver.find_element(By.CSS_SELECTOR, ".alert")
                assert alert.text == "mb11@qa.qa is already registered"
        else:
            allure.step(f"Регистрация по рандомным корректным данным")

    @allure.title("Страница авторизации")
    @allure.description("1. попробовать авторизоваться с некорректной парой email/пароль"
                        "2. авторизоваться с корректным значением email/пароль"
                        "3. сравнить значение cookies[‘access_token’] до и после успешной авторизации. Должны быть разные")
    @pytest.mark.parametrize("email, password", [("UnexistedEmailIHope@qa.qa", "qwerty"), ("mb11@qa.qa", "qwerty")])
    def test_auth(self, email, password):
        # Переход на страницу авторизации
        driver.get(self.url)
        login_btn = driver.find_element(By.LINK_TEXT, "Signin")
        login_btn.click()

        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        login_form_btn = driver.find_element(By.CSS_SELECTOR, "#login-form .btn")

        if email == "UnexistedEmailIHope@qa.qa" and password == "qwerty":
            with allure.step("авторизация с некорректной парой email/пароль"):
                email_field.send_keys(email)
                pass_field.send_keys(password)
                login_form_btn.click()
                alert = driver.find_element(By.CSS_SELECTOR, ".alert")
                assert alert.text == "email or password does not match"
        if email == "mb11@qa.qa" and password == "qwerty":
            with allure.step("авторизация с корректным email и паролем"):
                email_field.send_keys(email)
                pass_field.send_keys(password)
                login_form_btn.click()
                time.sleep(2)
                cookie_before_login = driver.get_cookie("access_token")["value"]
                driver.back()
                login_btn = driver.find_element(By.LINK_TEXT, "Signin")
                login_btn.click()
                time.sleep(2)
                cookie_after_login = driver.get_cookie("access_token")["value"]
            with allure.step("сравнить значение cookies[‘access_token’] до и после успешной авторизаци"):
                assert cookie_before_login != cookie_after_login
                print(cookie_before_login, cookie_after_login)

    @allure.title("Страница профиля")
    @allure.description("1. создать 3 сервера, проверить количество серверов на странице"
                        "2. удалить 1 сервер, проверить количество серверов на странице"
                        "3. создать сервер где cpu равно не числу, а строке, например “XEON”"
                        "4. создать сервер с некорректным доменом, проверить ответ по всплывающему сообщению.")
    def test_profile(self):
        #Переход на страницу логина
        driver.get(self.url)
        login_btn = driver.find_element(By.LINK_TEXT, "Signin")
        login_btn.click()

        #Логин с корректными данными
        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        login_form_btn = driver.find_element(By.CSS_SELECTOR, "#login-form .btn")
        email_field.send_keys("mb11@qa.qa")
        pass_field.send_keys("qwerty")
        login_form_btn.click()

        with allure.step("создать 3 сервера"):
            count = 0
            for i in range(0, 3):
                count += 1
                time.sleep(1)
                order_server_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-12 button")))
                order_server_btn.click()

                cpu_field = driver.find_element(By.CSS_SELECTOR, "#cpu")
                cpu_field.clear()
                cpu_field.send_keys(count)
                time.sleep(1)
                btn_order_modal = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-content .btn")))
                domain_field = driver.find_element(By.CSS_SELECTOR, "#info_url")
                domain_field.clear()
                domain_field.send_keys("https://www.google.com")
                btn_order_modal.click()
        with allure.step("проверить количество серверов на странице"):
            time.sleep(1)
            server_list = driver.find_elements(By.CSS_SELECTOR, "#server-list > div")
            assert len(server_list) == 3
        with allure.step("удалить 1 сервер, проверить количество серверов на странице"):
            del_serv_data = driver.find_element(By.CSS_SELECTOR, ".btn.del-server-btn")
            del_serv_data.click()
            driver.switch_to.alert.accept()
            time.sleep(1)
            server_list = driver.find_elements(By.CSS_SELECTOR, "#server-list > div")
            assert len(server_list) == 2

        with allure.step("создать сервер где cpu равно не числу, а строке, например “XEON”"):
            time.sleep(1)
            order_server_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-12 button")))
            order_server_btn.click()

            cpu_field = driver.find_element(By.CSS_SELECTOR, "#cpu")
            cpu_field.clear()
            cpu_field.send_keys("XEON")
            time.sleep(1)
            btn_order_modal = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-content .btn")))
            domain_field = driver.find_element(By.CSS_SELECTOR, "#info_url")
            domain_field.clear()
            domain_field.send_keys("https://www.google.com")
            btn_order_modal.click()

            alert = driver.find_element(By.CSS_SELECTOR, ".alert")
            assert alert.text == "Input payload validation failed"

        with allure.step("создать сервер с некорректным доменом"):
            cpu_field = driver.find_element(By.CSS_SELECTOR, "#cpu")
            cpu_field.clear()
            cpu_field.send_keys("12")
            time.sleep(1)
            btn_order_modal = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-content .btn")))
            domain_field = driver.find_element(By.CSS_SELECTOR, "#info_url")
            domain_field.clear()
            domain_field.send_keys("XEON")
            btn_order_modal.click()

            alert = driver.find_element(By.CSS_SELECTOR, ".alert")
            assert alert.text == "Input payload validation failed"

        time.sleep(5)

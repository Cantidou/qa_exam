import time
import pytest
import random
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


    def test_prices(self):
        cards_header = driver.find_elements(By.CSS_SELECTOR, "#Price .card-header")
        cards_text = driver.find_elements(By.CSS_SELECTOR, "#Price .card-text")
        cards_btn = driver.find_elements(By.CSS_SELECTOR, "#Price .btn")

        calc = lambda cpu, ram, ssd: cpu ** 2 + ram * 2 + ssd / 4
        data = {}

        def cards_data(headers, texts, btns):
            for i in range(len(headers)):
                split_text = texts[i].text.split("\n")
                data[headers[i].text] = split_text, btns[i].text.split(" ")[2]

        cards_data(cards_header, cards_text, cards_btn)

        for i in data:
            cpu = int(data[i][0][0].split(" ")[0])
            ram = int(data[i][0][1].split(" ")[0])
            ssd = int(data[i][0][2].split(" ")[0])
            price = int(data[i][1].split("$")[1])

            assert calc(cpu, ram, ssd) == price
            print(calc(cpu, ram, ssd))


    @pytest.mark.parametrize("email, password",
                             [("mb11@qa.qa", "   "), ("InvalidEmail", "qwerty"), ("mb11@qa.qa", "qwerty"),
                              (f"mb{random.randint(1, 99)}@qa.qa", "qwerty")])
    def test_register(self, email, password):
        register_btn = driver.find_element(By.LINK_TEXT, "Signup")
        register_btn.click()

        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        register_form_btn = driver.find_element(By.CSS_SELECTOR, "#registration-form .btn")

        email_field.send_keys(email)
        pass_field.send_keys(password)
        register_form_btn.click()

        if email == "mb11@qa.qa" and password == "   ":
            alert = driver.find_element(By.CSS_SELECTOR, ".alert")
            assert alert.text == "mb11@qa.qa is already registered"
        elif email == "InvalidEmail" and password == "qwerty":
            alert = driver.find_element(By.CSS_SELECTOR, ".alert")
            assert alert.text == "Input payload validation failed"
        elif email == "mb11@qa.qa" and password == "qwerty":
            alert = driver.find_element(By.CSS_SELECTOR, ".alert")
            assert alert.text == "mb11@qa.qa is already registered"


    @pytest.mark.parametrize("email, password", [("UnexistedEmailIHope@qa.qa", "qwerty"), ("mb11@qa.qa", "qwerty")])
    def test_auth(self, email, password):
        driver.get("http://127.0.0.1:5000/")
        login_btn = driver.find_element(By.LINK_TEXT, "Signin")
        login_btn.click()

        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        login_form_btn = driver.find_element(By.CSS_SELECTOR, "#login-form .btn")

        if email == "mb11@qa.qa" and password == "qwerty":
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

            assert cookie_before_login != cookie_after_login
            print(cookie_before_login, cookie_after_login)

    def test_profile(self):
        driver.get("http://127.0.0.1:5000/")
        login_btn = driver.find_element(By.LINK_TEXT, "Signin")
        login_btn.click()

        email_field = driver.find_element(By.CSS_SELECTOR, "#email")
        pass_field = driver.find_element(By.CSS_SELECTOR, "#password")
        login_form_btn = driver.find_element(By.CSS_SELECTOR, "#login-form .btn")
        email_field.send_keys("mb11@qa.qa")
        pass_field.send_keys("qwerty")
        login_form_btn.click()

        count = 0
        for i in range(0, 3):
            count += 1
            time.sleep(1)
            order_server_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-12 button")))
            order_server_btn.click()

            cpu_field = driver.find_element(By.CSS_SELECTOR, "#cpu")
            cpu_field.clear()
            cpu_field.send_keys(count)
            time.sleep(1)
            btn_order_modal = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-content .btn")))
            domain_field = driver.find_element(By.CSS_SELECTOR, "#info_url")
            domain_field.clear()
            domain_field.send_keys("https://www.google.com")
            btn_order_modal.click()

        time.sleep(1)
        server_list = driver.find_elements(By.CSS_SELECTOR, "#server-list > div")
        assert len(server_list) == 3


        del_serv_data = driver.find_element(By.CSS_SELECTOR, ".btn.del-server-btn")
        del_serv_data.click()
        driver.switch_to.alert.accept()
        time.sleep(1)
        server_list = driver.find_elements(By.CSS_SELECTOR, "#server-list > div")
        assert len(server_list) == 2

        time.sleep(1)
        order_server_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-12 button")))
        order_server_btn.click()

        cpu_field = driver.find_element(By.CSS_SELECTOR, "#cpu")
        cpu_field.clear()
        cpu_field.send_keys("XEON")
        time.sleep(1)
        btn_order_modal = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-content .btn")))
        domain_field = driver.find_element(By.CSS_SELECTOR, "#info_url")
        domain_field.clear()
        domain_field.send_keys("https://www.google.com")
        btn_order_modal.click()

        alert = driver.find_element(By.CSS_SELECTOR, ".alert")
        assert alert.text == "Input payload validation failed"

        #Wrong domain
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
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def testing():
    pytest.driver = webdriver.Chrome('c:/path/to/chromedriver.exe')
    # Переходим на странице авторизации
    pytest.driver.get('http://petfriends1.herokuapp.com/login')

    yield

    pytest.driver.quit()

def test_card_pets():
    """Проверка карточек притомцев, в списке: все притомцы /all_pets"""

    # Вводим email
    pytest.driver.find_element_by_id('email').send_keys('alone.test1@mail.ru')
    # Вводим пароль
    pytest.driver.find_element_by_id('pass').send_keys('1234')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"

    """Добавляем неявное ожидание, загрузки всех карточек питомцев на странице /all_pets"""
    try:
        pytest.driver.implicitly_wait(10)
        card_element_wait = pytest.driver.find_element_by_css_selector(".card-deck")  # неявное ожидание
        card_element_wait
    except TimeoutException:
        print("время ожидания загрузки карточек ВЫШЛО!")
        pytest.driver.quit()

    images = pytest.driver.find_elements_by_css_selector('.card-deck .card-img-top')
    names = pytest.driver.find_elements_by_css_selector('.card-deck .card-title')
    descriptions = pytest.driver.find_elements_by_css_selector('.card-deck .card-text')

    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ',' in descriptions[i].text
        parts = descriptions[i].text.split(",")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0

def test_card_list_my_pets():
    """Проверка количества карточек притомцев, в списке: мои притомцы /my_pets, """
    # Вводим email
    pytest.driver.find_element_by_id('email').send_keys('alone.test1@mail.ru')
    # Вводим пароль
    pytest.driver.find_element_by_id('pass').send_keys('1234')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"

    # Переходим на страницу /my_pets
    pytest.driver.find_element_by_css_selector('[href="/my_pets"]').click()

    """Добавляем явное ожидание загрузки таблицы с питомцами на странице  /my_pets"""
    try:
        element_table_wait = WebDriverWait(pytest.driver, 10).until(
            EC.presence_of_element_located((By.ID, "all_my_pets")))  # Явное ожидание
        element_table_wait
    except TimeoutException:
        print("время ожидания вышло")
        pytest.driver.quit()

    # Запрашиваем статистику пользователя, в которой содержится кол-во питомцев
    amount_my_pets = pytest.driver.find_element_by_xpath('//div[@class=".col-sm-4 left"]')

    # записываем в переменную элементы tr(в них карточки питомцев) в теге tbody
    list_my_pets = pytest.driver.find_elements_by_css_selector('tbody tr')  # tbody tr

    # Запрашиваем данные для получения фото питомцев, и циклом сохраняем их в список image_list
    image = pytest.driver.find_elements_by_css_selector('tbody th img')
    image_list = []
    for i in image:  # цикл для получения base64
        image_list.append(i.get_property("src"))

    # Запрашиваем данные имён, породы, возраста питомцев
    name = pytest.driver.find_elements_by_xpath('//*[@id="all_my_pets"]//td[1]')
    species = pytest.driver.find_elements_by_xpath('//*[@id="all_my_pets"]//td[2]')
    age = pytest.driver.find_elements_by_xpath('//*[@id="all_my_pets"]//td[3]')

    def names(num):
        """Функция для созданяи списка значений из полученных данных"""
        num_list = []
        for i_num in num:
            num_list.append(i_num.text)
        return num_list

    # Создаём списки с именами, породой, возрастом всех питомцев при помощи функции names
    name_list, species_list, age_list = names(name), names(species), names(age)

    # Сравниваем длинну списка элементов и количество питомцев из карточки пользователя amount_my_pets
    assert len(list_my_pets) == int(amount_my_pets.text.split()[2])

    assert len(image_list) == len(set(image_list))  # Проверяем повторяющиеся фото
    assert int(amount_my_pets.text.split()[2]) > len(
        image_list) / 2  # Проверяем что хотя бы у половины питомцев есть фото
    assert int(amount_my_pets.text.split()[2]) == len(
        name_list) and name_list != ''  # Проверяем что у всех питомцев есть имена
    assert int(amount_my_pets.text.split()[2]) == len(
        species_list) and species_list != ''  # Проверяем что у всех питомцев есть порода
    assert int(amount_my_pets.text.split()[2]) == len(
        age_list) and age_list != ''  # Проверяем что у всех питомцев есть аозраст
    assert len(name_list) == len(set(name_list))  # Проверяем повторяющиеся имена
    """подготовка к проверке повторяющихся питомцев"""
    list_zip = []  # переменная для сохранения результата работы функции zip()
    matrix = []  # Переменная для сохранения матрицы списка питомцев
    # Используем функцию zip() для разбивки списков имен,породы,возраста
    for i in zip(name_list, species_list, age_list):
        list_zip.append(i)

    for j in list_zip:  # Создаём матрицу из списков питомцев, каждый питомец в отдельном списке
        matrix.append(list(j))

    for i in range(len(matrix)):  # Цикл для поиска повторяющихся списков в матрице списков
        for j in range(len(matrix) - i - 1):
            if matrix[j] != matrix[j + 1]:
                matrix[j], matrix[j + 1] = matrix[j + 1], matrix[j]
            else:
                raise Exception(f'Повторяющийся питомцец: {matrix[j]}')
    assert not Exception  # Проверка вызова исклюения в случае нахождения повторяющихся питомцев




from selenium import webdriver

IMPLICIT_WAIT_TIME=6 # default time to wait to locate DOM elements, in seconds

def connect(host, username, password):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    # init driver
    driver = webdriver.Chrome(chrome_options=options)

    # doesn't work with self-generated CA's SSL certificate
    # TODO find why https doesn't frikking work!
    driver.get('http://' + host)

    # wait up to 10 seconds for the elements to become available
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)

    driver.switch_to.frame(driver.find_element_by_css_selector('#MAINFRAME'));

    # use css selectors to grab the login inputs
    input_username = driver.find_element_by_css_selector('input#login_username')
    input_password = driver.find_element_by_css_selector('input#login_password')
    input_login = driver.find_element_by_css_selector('input#LOGIN_VALUE_1')

    # fill input fields
    input_username.send_keys(username)
    input_password.send_keys(password)
    input_login.click()

    # TODO add "wrong password/username" handling
    # wait until LN_REMOTE_CONTROL appears
    # if not, if #msglbl contains 'Invalid Authentication'
    # ------- returns error




    # connected, going to remote control
    driver.find_element_by_css_selector(
        '#LN_REMOTE_CONTROL'
    ).click()

    driver.find_element_by_css_selector(
        '#LN_REMOTE_CONTROL_menu a[href="../page/server_power_control.html"]'
    ).click()

    # access to remote control form
    driver.switch_to.frame(driver.find_element_by_css_selector('#pageFrame'))

    status_str = driver.find_element_by_css_selector('#_statusMsg').text

    reset = driver.find_element_by_css_selector('input#_resetSrvr')
    poweroff = driver.find_element_by_css_selector('input#_iPwrOffSrvr')
    shutdown = driver.find_element_by_css_selector('input#_oPwrOffSrvr')
    poweron = driver.find_element_by_css_selector('input#_pwrOnSrvr')
    powercycle = driver.find_element_by_css_selector('input#_pwrCycleSrvr')

    action_button = driver.find_element_by_css_selector('input#_prfmAction')

    ### TODO
    ### action execution depending on the order, eg
    ### poweron.click() (possible only if status_str == "Host is down", check if radio is disabled="")
    ### action_button.click()
    ### then wait using selenium.webdriver.support.wait.WebDriverWait
    ### while displaying:
    ### driver.switch_to.frame(driver.find_element_by_css_selector('#MAINFRAME'));
    ### driver.find_element_by_css_selector('span#_loaderStatus').text

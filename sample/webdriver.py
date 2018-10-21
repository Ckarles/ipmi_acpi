from selenium import webdriver
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

WAIT_TIME_IMPLICIT=7 # default wait time to locate DOM elements, in seconds
WAIT_TIME_REMOTE_CMD=60 # timeout for a remote cmd

def switch_to_frame(driver, frame_name):
    driver.switch_to.default_content()
    if frame_name == 'pageframe':
        driver.switch_to.frame(driver.find_element_by_css_selector('#MAINFRAME'))
        driver.switch_to.frame(driver.find_element_by_css_selector('#pageFrame'))
    elif frame_name == 'headframe':
        driver.switch_to.frame(driver.find_element_by_css_selector('#HEADERFRAME'))
    else:
        driver.switch_to.frame(driver.find_element_by_css_selector('#MAINFRAME'))


class Caravel(object):
    def __init__(self, host, username, password):
        self.url = 'http://' + host
        self.username = username
        self.password = password

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        # init driver
        self.driver = webdriver.Chrome(chrome_options=options)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.disconnect()

    def connect(self):
        """browse the webpage and try to login"""
        driver = self.driver

        # doesn't work with self-generated CA's SSL certificate
        # TODO find why https doesn't frikking work!
        driver.get(self.url)

        # TODO check if host is accessible
        # note:
        # cannot get status code of request
        # try: ...ing to switch to frame as a workaround

        # wait up to X seconds for the elements to become available
        driver.implicitly_wait(WAIT_TIME_IMPLICIT)

        try:
            switch_to_frame(driver, 'mainframe')
        except selenium_exceptions.NoSuchElementException as e:
            raise RuntimeError('Cannot connect, unknown error.')

        # use css selectors to grab the login inputs
        input_username = driver.find_element_by_css_selector('input#login_username')
        input_password = driver.find_element_by_css_selector('input#login_password')
        input_login = driver.find_element_by_css_selector('input#LOGIN_VALUE_1')

        # fill input fields
        input_username.send_keys(self.username)
        input_password.send_keys(self.password)
        input_login.click()

        if not self.is_connected():
            switch_to_frame(driver,'mainframe');
            if 'Invalid Authentication' in driver.find_element_by_css_selector('#msglbl').text:
                raise ValueError('Username/password credentials invalid.')
            else:
                raise RuntimeError('Cannot connect, unknown error.')

    def disconnect(self):
        """disconnects the driver"""
        self.driver.close()

    def is_connected(self):
        """return true if username is connected"""
        switch_to_frame(self.driver,'headframe')

        try:
            return self.username in self.driver.find_element_by_css_selector('#username').text
        except:
            return False

    def go_to_remote_control(self):
        """drive the caravel to remote control"""
        driver = self.driver

        if not self.is_connected():
            raise RuntimeError('Cannot access remote control, driver not connected.')

        switch_to_frame(driver,'mainframe')

        # going to remote control
        driver.find_element_by_css_selector(
            '#LN_REMOTE_CONTROL'
        ).click()

        driver.find_element_by_css_selector(
            '#LN_REMOTE_CONTROL_menu a[href="../page/server_power_control.html"]'
        ).click()

        if not self.is_on_remote_control():
            raise RuntimeError('Cannot access remote control, unknown error.')

    def is_on_remote_control(self):
        """return true if status message is showing"""

        switch_to_frame(self.driver,'pageframe')

        try:
            return isinstance(self.driver.find_element_by_css_selector('#_statusMsg').text, str)
        except:
            return False


class RemoteControl(object):
    def __init__(self, caravel):
        self.caravel = caravel

        # ensure we're at the right place
        if not caravel.is_on_remote_control():
            caravel.go_to_remote_control()

    def status(self, print_cb=None):
        switch_to_frame(self.caravel.driver, 'pageframe')
        status = self.caravel.driver.find_element_by_css_selector('#_statusMsg').text
        if print_cb:
            print_cb(status)
        return status


def add_remote_cmd(cmd, selector):
    def fn(self, print_cb=print):
        driver = self.caravel.driver
        switch_to_frame(driver, 'pageframe')

        el = driver.find_element_by_css_selector(selector)

        if not el.is_enabled():
            status = self.status()
            raise ValueError('Cannot {0}, status: "{1}"'.format(cmd, status))
        else:
            print_cb('Ipmi status: {}'.format(self.status()))
            el.click()
            driver.find_element_by_css_selector('input#_prfmAction').click()

            try:
                watch_remote_cmd_state(driver, print_cb)
            except selenium_exceptions.TimeoutException as e:
                return print_cb('Error: command taking more than {}s to execute. Cannot confirm state.'.format(WAIT_TIME_REMOTE_CMD))

            print_cb('Ipmi status: {}'.format(self.status()))

    setattr(RemoteControl, cmd, fn)

command_selector = {
    'reset':        'input#_resetSrvr',
    'force-stop':   'input#_iPwrOffSrvr',
    'stop':         'input#_oPwrOffSrvr',
    'start':        'input#_pwrOnSrvr',
    # wtf is powercycle ?
    # 'cycle':        'input#_pwrCycleSrvr'
}

for command, selector in command_selector.items():
    add_remote_cmd(command, selector)

class text_reach(object):
    def __init__(self, locator, text_to_reach, callback):
        self.locator = locator
        self.text_to_reach = text_to_reach
        self.callback = callback
        self.text = ''

    def __call__(self, driver):
        actual_text = driver.find_element(*self.locator).text

        if actual_text != self.text:
            if actual_text:
                self.callback(actual_text)
            self.text = actual_text
            return self.text == self.text_to_reach
        else:
            return False

def watch_remote_cmd_state(driver, callback):
    switch_to_frame(driver, 'mainframe')
    WebDriverWait(driver, WAIT_TIME_REMOTE_CMD).until(text_reach(
        (By.CSS_SELECTOR, 'span#_loaderStatus'),
        '',
        callback
    ))

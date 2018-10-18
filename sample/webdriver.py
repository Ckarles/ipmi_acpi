from selenium import webdriver

IMPLICIT_WAIT_TIME=7 # default time to wait to locate DOM elements, in seconds

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

        # TODO check if host is accessible

        # doesn't work with self-generated CA's SSL certificate
        # TODO find why https doesn't frikking work!
        driver.get(self.url)

        # wait up to 10 seconds for the elements to become available
        driver.implicitly_wait(IMPLICIT_WAIT_TIME)

        switch_to_frame(driver, 'mainframe')

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

    ### TODO
    ### action execution depending on the order, eg
    ### poweron.click() (possible only if status_str == "Host is down", check if radio element.is_enabled() (or is_selected ?))
    ### action_button.click()
    ### then wait using selenium.webdriver.support.wait.WebDriverWait
    ### while displaying:
    ### driver.switch_to.frame(driver.find_element_by_css_selector('#MAINFRAME'));
    ### driver.find_element_by_css_selector('span#_loaderStatus').text

class RemoteControl(object):
    def __init__(self, caravel):
        self.caravel = caravel

        # ensure we're at the right place
        if not caravel.is_on_remote_control():
            caravel.go_to_remote_control()

    def status(self):
        switch_to_frame(self.caravel.driver, 'pageframe')
        return self.caravel.driver.find_element_by_css_selector('#_statusMsg').text


def add_remote_cmd(cmd, selector):
    def fn(self):
        switch_to_frame(self.caravel.driver, 'pageframe')

        el = self.caravel.driver.find_element_by_css_selector(selector)

        if not el.is_enabled():
            status = self.status()
            raise ValueError('Cannot {0}, status: "{1}"'.format(cmd, status))
        else:
            el.click()
            self.caravel.driver.find_element_by_css_selector('input#_prfmAction').click()

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

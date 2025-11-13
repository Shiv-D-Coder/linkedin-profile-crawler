from dataclasses import dataclass
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Experience:
    position_title: str = None
    institution_name: str = None
    from_date: str = None
    to_date: str = None
    duration: str = None
    location: str = None
    description: str = None
    linkedin_url: str = None


@dataclass
class Education:
    institution_name: str = None
    degree: str = None
    from_date: str = None
    to_date: str = None
    description: str = None
    linkedin_url: str = None


class Scraper:
    WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        try:
            self.driver.execute_script('alert("Focus window")')
            self.driver.switch_to.alert.accept()
        except:
            pass

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((by, name))
        )

    def is_signed_in(self):
        try:
            # Check if we're on the feed page (logged in)
            return "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url
        except:
            return False

    def scroll_to_half(self):
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

    def scroll_to_bottom(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
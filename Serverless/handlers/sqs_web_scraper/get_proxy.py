import threading
import time

from interfaces.api_phase import CloudFunctionPhase
from bs4 import BeautifulSoup as soup
import random
import requests


class GetProxy(CloudFunctionPhase):
    """
    Proxy gathering object class, responsible for locating and selecting a viable proxy for web scraping operations.
    """

    FREE_PROXIES_SOURCE_URL = 'https://free-proxy-list.net/'
    PROXY_TEST_URL = 'https://httpbin.org/ip'
    CONNECTION_ATTEMPTS_TIME_OUT = 10

    def __init__(self, invocation_id):
        """
        Constructor of the Validation object, stores acquired data.
        """

        self.proxies = []
        self.selected_proxy = None
        self.lock = threading.Lock()
        self.timeout_flag = False

        # Initializes APIPhase superclass parameters and procedures
        super(GetProxy, self).__init__(prefix='GP', phase_name='Get proxy', invocation_id=invocation_id)

    def run(self) -> bool:

        self.__get_proxies()
        self.__find_proxy()

        return True

    def __get_proxies(self):

        try:
            response = requests.get(self.FREE_PROXIES_SOURCE_URL)
        except Exception as e:
            self.log(self.rsc.UNABLE_TO_CONNECT_TO_PROXIES_PROVIDER.format(self.FREE_PROXIES_SOURCE_URL, str(e)))
            return False

        page_html = response.text
        page_soup = soup(page_html, "html.parser")
        containers = page_soup.find_all("div", {"class": "table-responsive"})[0]
        ip_index = [8 * k for k in range(80)]
        proxies = set()

        for i in ip_index:
            ip = containers.find_all("td")[i].text
            port = containers.find_all("td")[i + 1].text
            https = containers.find_all("td")[i + 6].text

            if https == 'yes':
                proxy = 'https://' + ip + ':' + port
                proxies.add(proxy)

        proxies = list(proxies)
        random.shuffle(proxies)
        self.proxies = proxies

        self.log(self.rsc.PROXIES_FOUND.format(str(len(self.proxies))))
        return True

    def __find_proxy(self):
        for x in range(5):
            t = threading.Thread(target=self.__check_proxies)
            t.daemon = True
            t.start()

        ts = time.time()
        while self.proxies and not self.selected_proxy and (time.time()-ts) < self.CONNECTION_ATTEMPTS_TIME_OUT:
            time.sleep(0.2)

        if(time.time()-ts) >= self.CONNECTION_ATTEMPTS_TIME_OUT:
            self.log(self.rsc.PROXY_ATTEMPTS_TIMED_OUT)
            self.timeout_flag = True
        elif self.selected_proxy:
            self.log(self.rsc.PROXY_SELECTED.format(str(self.selected_proxy)))
        else:
            self.log(self.rsc.PROXY_UNABLE_TO_QUALIFY)

    def __check_proxies(self):
        while True:
            self.lock.acquire()
            if len(self.proxies) == 0 or self.timeout_flag: break
            proxy = self.proxies.pop(0)
            self.log(self.rsc.PROXY_ATTEMPTING_CONNECTION.format(str(proxy)))
            self.lock.release()
            if self.selected_proxy: break
            try:
                response = requests.get(self.PROXY_TEST_URL, proxies={"http": proxy, "https": proxy}, timeout=5)
                self.lock.acquire()
                if self.timeout_flag: break
                if not self.selected_proxy:
                    self.selected_proxy = proxy
                self.lock.release()
            except Exception as e:
                self.lock.acquire()
                if self.timeout_flag: break
                if not self.selected_proxy:
                    self.log(self.rsc.PROXY_SKIPPED.format(str(proxy), str(e)))
                self.lock.release()






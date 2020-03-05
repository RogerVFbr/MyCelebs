import threading, time, random, requests

from interfaces.cloud_function_phase import CloudFunctionPhase
from bs4 import BeautifulSoup as soup


class GetProxy(CloudFunctionPhase):
    """
    Proxy gathering object class, responsible for locating and selecting a viable proxy for web scraping operations.
    """

    FREE_PROXIES_SOURCE_URL = 'https://free-proxy-list.net/'
    PROXY_TEST_URL = 'https://httpbin.org/ip'
    CONNECTION_ATTEMPTS_TIME_OUT = 15
    PROXY_CHECKER_WORKERS = 10

    def __init__(self, invocation_id):
        """
        Constructor of the Validation object, stores acquired data.
        """

        self.proxies = []
        self.proxies_to_evaluate = []
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

        ts_request = time.time()

        try:
            response = requests.get(self.FREE_PROXIES_SOURCE_URL, timeout=5)
        except Exception as e:
            te_request = str(round(time.time() - ts_request, 3)) + 's'
            self.log(self.rsc.UNABLE_TO_CONNECT_TO_PROXIES_PROVIDER.format(self.FREE_PROXIES_SOURCE_URL, te_request,
                                                                           str(e)))
            return False

        te_request = str(round(time.time() - ts_request, 3)) + 's'
        ts_parsing = time.time()

        page_html = response.text
        page_soup = soup(page_html, "html.parser")
        containers = page_soup.find("div", {"class": "table-responsive"})
        ip_index = [8 * k for k in range(80)]
        proxies = set()

        ip_containers = containers.find_all("td")

        for i in ip_index:

            ip = ip_containers[i].text
            port = ip_containers[i + 1].text
            https = ip_containers[i + 6].text

            if https == 'yes':
                proxy = 'https://' + ip + ':' + port
                proxies.add(proxy)

        te_parsing = str(round(time.time() - ts_parsing, 3)) + 's'

        proxies = list(proxies)
        random.shuffle(proxies)
        self.proxies = proxies

        self.log(self.rsc.PROXIES_FOUND.format(str(len(self.proxies)), self.FREE_PROXIES_SOURCE_URL, te_request,
                                               te_parsing))
        return True

    def __find_proxy(self):
        ts = time.time()
        self.proxies_to_evaluate = self.proxies[:]

        for x in range(self.PROXY_CHECKER_WORKERS):
            t = threading.Thread(target=self.__check_proxies)
            t.daemon = True
            t.start()

        while self.proxies_to_evaluate \
                and not self.selected_proxy \
                and (time.time() - ts) < self.CONNECTION_ATTEMPTS_TIME_OUT:
            time.sleep(0.2)

        te = str(round(time.time() - ts, 3)) + 's'
        if(time.time()-ts) >= self.CONNECTION_ATTEMPTS_TIME_OUT:
            self.log(self.rsc.PROXY_ATTEMPTS_TIMED_OUT.format(te))
            self.timeout_flag = True
        elif self.selected_proxy:
            self.log(self.rsc.PROXY_SELECTED.format(str(self.selected_proxy), self.proxies.index(self.selected_proxy),
                                                    str(len(self.proxies) - len(self.proxies_to_evaluate)), te))
        else:
            self.log(self.rsc.PROXY_UNABLE_TO_QUALIFY.format(te))

    def __check_proxies(self):
        while True:
            self.lock.acquire()
            if len(self.proxies_to_evaluate) == 0 or self.timeout_flag: break
            proxy = self.proxies_to_evaluate.pop(0)
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
                pass








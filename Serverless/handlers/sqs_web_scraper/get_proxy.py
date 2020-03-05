import threading, time, random, requests

from requests.exceptions import *

from interfaces.cloud_function_phase import CloudFunctionPhase
from bs4 import BeautifulSoup as soup


class GetProxy(CloudFunctionPhase):
    """
    Proxy gathering object class, responsible for locating and selecting a viable proxy for web scraping operations.
    """

    PROXY_TEST_URL = 'https://httpbin.org/ip'
    PROCEDURE_TIMEOUT = 15
    PROXY_CHECKER_WORKERS = 20

    def __init__(self, invocation_id):
        """
        Constructor of the Validation object, stores acquired data.
        """

        self.proxies = []
        self.proxies_to_evaluate = []
        self.attempt = []
        self.selected_proxy = None
        self.lock = threading.Lock()
        self.abort_workers_flag = False
        self.proxy_lists = [
            ('https://free-proxy-list.net/', self.__scrap_free_proxy_list),
            ('http://nntime.com/', self.__scrap_nn_time)
        ]
        self.unreachable_proxy_list_count = 0
        self.ts_procedure = time.time()
        self.ts_proxy_check = None

        # Initializes APIPhase superclass parameters and procedures
        super(GetProxy, self).__init__(prefix='GP', phase_name='Get proxy', invocation_id=invocation_id)

    def run(self) -> bool:

        self.__launch_checkers()
        self.__launch_scrapers()
        self.__evaluate()
        return True

    def __launch_checkers(self):
        for x in range(self.PROXY_CHECKER_WORKERS):
            t = threading.Thread(target=self.__checker_worker)
            t.daemon = True
            t.start()

    def __launch_scrapers(self):
        for p in self.proxy_lists:
            t = threading.Thread(target=self.__scrap_list, args=(p[0], p[1]))
            t.daemon = True
            t.start()

    def __scrap_list(self, url, scraper):
        """
        Scraps a given proxy addresses website, given by URL and scraping function.
        :param url: URL of the proxy finder.
        :param scraper: scraping function adapted the particular website.
        :return: void.
        """

        ts_request = time.time()

        try:
            response = requests.get(url, timeout=5)
        except Exception as e:
            te_request = str(round(time.time() - ts_request, 3)) + 's'
            self.lock.acquire()
            self.log(self.rsc.UNABLE_TO_CONNECT_TO_PROXIES_PROVIDER.format(url, te_request,
                                                                           str(e)))
            self.unreachable_proxy_list_count += 1
            self.lock.release()
            return

        te_request = str(round(time.time() - ts_request, 3)) + 's'
        ts_parsing = time.time()

        if self.selected_proxy or self.abort_workers_flag: return
        page_html = response.text
        page_soup = soup(page_html, "html.parser")
        proxy_count = 0

        try:
            proxies = scraper(page_soup)
            for proxy in proxies:
                self.lock.acquire()
                if self.selected_proxy or self.abort_workers_flag: return
                if self.__address_validator(proxy) and proxy not in self.proxies:
                    self.proxies.append(proxy)
                    self.proxies_to_evaluate.append(proxy)
                    proxy_count += 1
                self.lock.release()
        except Exception as e:
            self.log(self.rsc.UNABLE_TO_SCRAP.format(url, str(e)))

        te_parsing = str(round(time.time() - ts_parsing, 3)) + 's'

        self.lock.acquire()
        if not self.selected_proxy:
            self.log(self.rsc.PROXIES_FOUND.format(str(proxy_count), url, te_request, te_parsing))
        self.lock.release()

    @staticmethod
    def __scrap_nn_time(page_soup):

        decoder_raw = page_soup.find_all("script", {"type": "text/javascript"})
        decoder = decoder_raw[1].text.strip().split(';')
        decoder_dict = {x.split('=')[0]: x.split('=')[1] for x in decoder if x}
        rows = page_soup.find_all("tr", {"class": ["odd", "even"]})

        for x in rows:
            cells = x.find_all('td')
            data = cells[1].text.replace(')', '').split('document.write(":"+')
            ip = data[0]
            port = ''.join([decoder_dict[x] for x in data[1].replace('+', '')])
            proxy = f'https://{ip}:{port}'
            yield proxy

    @staticmethod
    def __scrap_free_proxy_list(page_soup):

        containers = page_soup.find("div", {"class": "table-responsive"})
        ip_index = [8 * k for k in range(80)]
        ip_containers = containers.find_all("td")

        for i in ip_index:
            ip = ip_containers[i].text
            port = ip_containers[i + 1].text
            https = ip_containers[i + 6].text
            if https != 'yes': continue
            proxy = 'https://' + ip + ':' + port
            yield proxy

    def __evaluate(self):

        te_procedure = time.time() - self.ts_procedure
        while not self.selected_proxy \
                and te_procedure <= self.PROCEDURE_TIMEOUT \
                and self.unreachable_proxy_list_count < len(self.proxy_lists):
            time.sleep(0.2)
            te_procedure = time.time() - self.ts_procedure

        self.abort_workers_flag = True

        if self.ts_proxy_check:
            te_proxy_check = str(round(time.time() - self.ts_proxy_check, 3)) + 's'
        else:
            te_proxy_check = 'N.A.'

        if self.selected_proxy:
            self.log(self.rsc.PROXY_SELECTED.format(str(self.selected_proxy), self.attempt.index(self.selected_proxy)+1,
                                                    str(len(self.proxies) - len(self.proxies_to_evaluate)),
                                                    te_proxy_check))
        elif te_procedure > self.PROCEDURE_TIMEOUT:
            self.log(self.rsc.PROXY_ATTEMPTS_TIMED_OUT.format(te_proxy_check))
        elif self.unreachable_proxy_list_count < len(self.proxy_lists):
            self.log(self.rsc.PROXY_PROVIDERS_UNREACHABLE.format(te_proxy_check))
        else:
            self.log(self.rsc.PROXY_UNABLE_TO_QUALIFY.format(te_proxy_check))

    def __checker_worker(self):
        while True:
            if self.selected_proxy or self.abort_workers_flag: return
            self.lock.acquire()
            if len(self.proxies_to_evaluate) == 0:
                self.lock.release()
                time.sleep(0.2)
                continue
            if not self.ts_proxy_check:
                self.ts_proxy_check = time.time()
            random_index = random.randint(0, len(self.proxies_to_evaluate)-1)
            proxy = self.proxies_to_evaluate.pop(random_index)
            self.attempt.append(proxy)
            # print('Attempting: ' + proxy)
            self.lock.release()
            try:
                _ = requests.get(self.PROXY_TEST_URL, proxies={"http": proxy, "https": proxy}, timeout=5)
                self.lock.acquire()
                # print('Success: ' + proxy)
                if self.selected_proxy or self.abort_workers_flag: return
                self.selected_proxy = proxy
                self.lock.release()
            except ConnectTimeout:
                self.lock.acquire()
                if not self.selected_proxy:
                    self.log(f"'{proxy}' timed out.")
                self.lock.release()
            except ProxyError:
                self.lock.acquire()
                if not self.selected_proxy:
                    self.log(f"'{proxy}' not contactable.")
                self.lock.release()
            except Exception as e:
                self.lock.acquire()
                if not self.selected_proxy:
                    self.log(f"'{proxy}' general exception: {str(e)}")
                self.lock.release()

    @staticmethod
    def __address_validator(proxy: str) -> bool:

        base = proxy.split('//')
        if len(base) != 2: return False
        if base[0] not in ['http:', 'https:']: return False

        address = base[1].split(':')
        if len(address) != 2: return False

        ip = address[0]
        port = address[1]

        ip_octets = ip.split('.')
        if len(ip_octets) != 4: return False

        try:
            ip_octets_numeric = [int(x) for x in ip_octets]
        except:
            return False

        for x in ip_octets_numeric:
            if 0 > x > 255: return False

        try:
            port_numeric = int(port)
        except:
            return False

        if 0 > port_numeric > 65535: return False

        return True


if __name__ == "__main__":
    _ = GetProxy('test_id_1')










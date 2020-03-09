import threading, time, random, requests
from requests.exceptions import *

from handlers.sqs_web_scraper.user_agent_randomizer import UserAgentRandomizer
from interfaces.cloud_function_phase import CloudFunctionPhase
from bs4 import BeautifulSoup


class GetProxy(CloudFunctionPhase):
    """
    Proxy gathering object class, responsible for locating and selecting viable proxies for web scraping operations.
    """

    PROXY_TEST_URL = 'https://httpbin.org/ip'       # :str: URL to test acquired proxies for connectivity.
    PROCEDURE_TIMEOUT = 15                          # :int: Maximum tolerated procedure duration in seconds.
    PROXY_CHECKER_WORKERS = 20                      # :int: Number of worker threads to test acquired proxies.
    NO_PROXIES_TO_GET = 1                           # :int: Amount of proxies to be acquired by procedure.

    def __init__(self, invocation_id):
        """
        Constructor of the proxy gathering object, stores acquired data.
        """

        self.proxies = []                           # :list: All unique proxies acquired by process.
        self.proxies_to_evaluate = []               # :list: Proxy addresses left to be evaluated.
        self.selected_proxies = []                  # :list: Proxy addresses confirmed to be working.
        self.lock = threading.Lock()                # :list: Lock for concurrent list operations and logging.
        self.abort_workers_flag = False             # :bool: Flag to signal operation end and threads shutdown.
        self.no_of_checked_proxy_lists = 0          # :int: Number of proxy lists currently contacted.
        self.no_of_checked_proxies = 0              # :int: Number of proxies checked.
        self.ts_procedure = time.time()             # :int: Full procedure start time.
        self.ts_proxy_check = None                  # :int: Start time of first proxy check.
        self.proxy_lists = {                        # :dict: Proxy list URLs and corresponding decoding methods.
            'https://www.us-proxy.org/': self.__scrap_free_proxy_list,
            'https://free-proxy-list.net/uk-proxy.html': self.__scrap_free_proxy_list,
            'https://proxygather.com/proxylist/country/?c=United%20States': self.__scrap_proxy_gather
            # 'https://free-proxy-list.net/anonymous-proxy.html': self.__scrap_free_proxy_list,
            # 'http://nntime.com/': self.__scrap_nn_time,
            # 'https://proxygather.com': self.__scrap_proxy_gather,
            # 'https://free-proxy-list.net/': self.__scrap_free_proxy_list,
        }


        # Initializes APIPhase superclass parameters and procedures
        super(GetProxy, self).__init__(prefix='GP', phase_name='Get proxy', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: launches proxy list scrapers and address checkers.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Launches proxy list scrapers.
        self.__launch_proxy_scrapers()

        # Launches acquired proxy addresses checker threads.
        self.__launch_checkers()

        # Awaits for results and evaluate.
        self.__await_results()
        return True

    def __launch_proxy_scrapers(self):
        """
        Launches proxy list scraping threads, responsible for acquiring proxy addresses to be later checked.
        :return: void.
        """

        for url, func in self.proxy_lists.items():
            t = threading.Thread(target=self.__scrap_list, args=(url, func))
            t.daemon = True
            t.start()

    def __launch_checkers(self):
        """
        Launches proxy address checker threads.
        :return:
        """

        for x in range(self.PROXY_CHECKER_WORKERS):
            t = threading.Thread(target=self.__checker_worker)
            t.daemon = True
            t.start()

    def __scrap_list(self, url, scraper):
        """
        Scraps proxy addresses list website, given by URL and scraping function.
        :param url: URL of the proxy list website.
        :param scraper: scraping function adapted to the particular website.
        :return: void.
        """

        # Attempts to contact proxy list website
        ts_request = time.time()
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except Exception as e:
            te_request = str(round(time.time() - ts_request, 3)) + 's'
            self.lock.acquire()
            self.log(self.rsc.UNABLE_TO_CONNECT_TO_PROXIES_PROVIDER.format(url, te_request,
                                                                           str(e)))
            self.no_of_checked_proxy_lists += 1
            self.lock.release()
            return

        # If contact was successful, parses content into BeautifulSoup object
        if len(self.selected_proxies) >= self.NO_PROXIES_TO_GET or self.abort_workers_flag: return
        te_request = str(round(time.time() - ts_request, 3)) + 's'
        ts_parsing = time.time()
        page_html = response.text
        page_soup = BeautifulSoup(page_html, "html.parser")
        proxy_count = 0

        # Iterates on associated scraping function (yield) to acquire proxy addresses.
        try:
            proxies = scraper(page_soup)
            for proxy in proxies:
                self.lock.acquire()
                if len(self.selected_proxies) >= self.NO_PROXIES_TO_GET or self.abort_workers_flag:
                    self.lock.release()
                    return
                if self.__address_validator(proxy) and proxy not in self.proxies:
                    self.proxies.append(proxy)
                    self.proxies_to_evaluate.append(proxy)
                    proxy_count += 1
                self.lock.release()
        except Exception as e:
            self.lock.acquire()
            self.log(self.rsc.UNABLE_TO_SCRAP.format(url, str(e)))
            self.lock.release()

        # Finishes procedure and informs developer of acquired results.
        te_parsing = str(round(time.time() - ts_parsing, 3)) + 's'
        self.lock.acquire()
        if len(self.selected_proxies) < self.NO_PROXIES_TO_GET:
            self.log(self.rsc.PROXIES_FOUND.format(str(proxy_count), url, te_request, te_parsing))
            self.no_of_checked_proxy_lists += 1
        self.lock.release()

    @staticmethod
    def __scrap_proxy_gather(page_soup: BeautifulSoup):
        """
        Scraping function associated with URL 'https://proxygather.com' and possible subdomains.
        :param page_soup: Parsed BeautifulSoup object.
        :return: iterator yielding proxy addresses.
        """

        table = page_soup.find("table", {"id": "tblproxy"})
        scripts = table.find_all("script")
        for i, x in enumerate(scripts):
            data = x.text.strip().replace('gp.insertPrx(', '').replace(')', '').replace('null', '"null"')\
                .replace(';', '')
            data = eval(data)
            ip = data['PROXY_IP']
            port = int(data['PROXY_PORT'], 16)
            address = f"https://{ip}:{port}"
            yield address

    @staticmethod
    def __scrap_nn_time(page_soup: BeautifulSoup):
        """
        Scraping function associated with URL 'http://nntime.com/' and possible subdomains.
        :param page_soup: Parsed BeautifulSoup object.
        :return: iterator yielding proxy addresses.
        """

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
    def __scrap_free_proxy_list(page_soup: BeautifulSoup):
        """
        Scraping function associated with URL 'https://free-proxy-list.net/' and possible subdomains.
        :param page_soup: Parsed BeautifulSoup object.
        :return: iterator yielding proxy addresses.
        """

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

    def __await_results(self):
        """
        Locks main thread to await list scraper and proxy checker results. Flags worker threads to stop when results
        are acquired and validated.
        :return: void.
        """

        te_procedure = time.time() - self.ts_procedure
        not_enough_proxies_found_yet, procedure_not_yet_timed_out = True, True
        all_proxy_lists_checked, no_proxies_left_to_evaluate = False, False

        while not_enough_proxies_found_yet \
                and procedure_not_yet_timed_out \
                and not (all_proxy_lists_checked and no_proxies_left_to_evaluate):
            time.sleep(0.2)
            te_procedure = time.time() - self.ts_procedure
            not_enough_proxies_found_yet = len(self.selected_proxies) < self.NO_PROXIES_TO_GET
            procedure_not_yet_timed_out = te_procedure <= self.PROCEDURE_TIMEOUT
            all_proxy_lists_checked = self.no_of_checked_proxy_lists == len(self.proxy_lists)
            no_proxies_left_to_evaluate = len(self.proxies) == self.no_of_checked_proxies

        self.abort_workers_flag = True

        if self.ts_proxy_check:
            te_proxy_check = str(round(time.time() - self.ts_proxy_check, 3)) + 's'
        else:
            te_proxy_check = 'N.A.'

        if len(self.selected_proxies) >= self.NO_PROXIES_TO_GET:
            self.log(self.rsc.PROXY_SELECTED.format(len(self.selected_proxies),
                                                    str(len(self.proxies) - len(self.proxies_to_evaluate)),
                                                    te_proxy_check))
        elif te_procedure > self.PROCEDURE_TIMEOUT:
            self.log(self.rsc.PROXY_ATTEMPTS_TIMED_OUT.format(len(self.selected_proxies), te_proxy_check))
        elif all_proxy_lists_checked and no_proxies_left_to_evaluate:
            self.log(self.rsc.NOTHING_MORE_TO_EVALUATE.format(te_proxy_check))

    def __checker_worker(self):
        """
        Worker thread to confirm acquired proxy URL is valid and currently working.
        :return: void.
        """

        while True:
            if len(self.selected_proxies) >= self.NO_PROXIES_TO_GET or self.abort_workers_flag: return
            self.lock.acquire()
            if len(self.proxies_to_evaluate) == 0:
                self.lock.release()
                time.sleep(0.05)
                continue
            if not self.ts_proxy_check:
                self.ts_proxy_check = time.time()
            random_index = random.randint(0, len(self.proxies_to_evaluate)-1)
            proxy = self.proxies_to_evaluate.pop(random_index)
            self.lock.release()
            proxies = {"http": proxy, "https": proxy}
            try:
                headers = {'User-Agent': UserAgentRandomizer.get()}
                response = requests.get(self.PROXY_TEST_URL, headers=headers, proxies=proxies, timeout=5)
                response.raise_for_status()
                self.lock.acquire()
                if len(self.selected_proxies) >= self.NO_PROXIES_TO_GET or self.abort_workers_flag:
                    self.lock.release()
                    return
                self.log(f"Acquired '{proxy}'.")
                self.selected_proxies.append(proxy)
                self.lock.release()
            except ConnectTimeout as e:
                self.lock.acquire()
                if len(self.selected_proxies) < self.NO_PROXIES_TO_GET:
                    self.log(f"'{proxy}' timed out.")
                self.lock.release()
            except ProxyError as e:
                self.lock.acquire()
                if len(self.selected_proxies) < self.NO_PROXIES_TO_GET:
                    self.log(f"'{proxy}' not contactable.")
                self.lock.release()
            except Exception as e:
                self.lock.acquire()
                if len(self.selected_proxies) < self.NO_PROXIES_TO_GET:
                    self.log(f"'{proxy}' exception: {str(e)}")
                self.lock.release()
            self.no_of_checked_proxies += 1

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
    GetProxy('test_id_1')










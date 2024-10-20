"""
네이버쇼핑 리뷰데이터 수집과 관련하여, 유틸리티 함수와 클래스를 제공한다.

함수 목록
1. `add_headers_randomly`
    기본 headers에 additional_headers를 추가로 1~n개 선택하여 추가한다.
2. `get_proxies_1`
    `https://free-proxy-list.net`로부터 프록시서버 URL을 가져온다.
3. `get_proxies_2`
    `https://proxyscrape.com/free-proxy-list?ref=ymmxztq&tm_subid1=free-proxy-server-list`로부터 프록시서버 URL을 가져온다.
"""

# lib
from lib.python.decorators import retry_with_delay

# default
import random
import numpy as np
import requests
from bs4 import BeautifulSoup as bs
import random

RETRY_COUNT = 10
DELAY_SECONDS = (7,10)
VERBOSE = 2
VERBOSE_PERIOD = 1

def add_headers_randomly(headers: dict, additional_headers: dict) -> dict:
    """
    기본 headers에 additional_headers를 추가로 1~n개 선택하여 추가한다.
    
    Args:
        headers (dict): 기본 headers.
        additional_headers (dict): 기본 headers 이외에, 추가입력되는 headers.
        
    Returns:
        dict: 기본 headers에 additional_headers를 추가로 1~n개 선택하여 추가 된 딕셔너리.
    """
    
    # 몇 개를 추가할지 정하고, 추가할 additional_headers에서의 인덱스를 가져온다.
    add_n = random.choice(range(1,len(additional_headers)+1))
    add_idx = np.random.choice(range(len(additional_headers)), size=add_n, replace=False)
    
    # headers에 추가할 additional_headers를 넣어준다.
    for idx in add_idx:
        key = [k for k,v in additional_headers.items()][idx]
        val = [v for k,v in additional_headers.items()][idx]
        headers[key] = val
        
    return headers

@retry_with_delay(retry_count=RETRY_COUNT, delay_seconds=DELAY_SECONDS, verbose=VERBOSE, verbose_period=VERBOSE_PERIOD)
def _get_proxies_1(verify: bool = True) -> list[str]:
    """
    `https://free-proxy-list.net`로부터 프록시서버 URL을 가져온다.
    
    **참조**
    1. https://jaehyojjang.dev/python/free-proxy-server/
    
    Args:
        verify (bool, optional): HTTPS 요청을 보낼 때 서버의 SSL 인증서를 검증할지 여부. default=True.
    
    Returns:
        list[str]: 프록시서버 URL로 이루어진 리스트.
    """
    
    free_proxy_server_url = 'https://free-proxy-list.net'
    
    resp = requests.get(url=free_proxy_server_url, verify=verify)
    soup = bs(resp.text,'html.parser')
    proxies_length = len(soup.select('table.table.table-striped.table-bordered > tbody > tr'))
    
    proxies_url = []
    for index in range(proxies_length):            
        proxies = soup.select('table.table.table-striped.table-bordered > tbody > tr')

        ## Code (한국만 가져올 경우)
        # code = proxies[index].select('td')[2].text.strip()
        # if code == 'KR':
        
        # Port
        port = proxies[index].select('td')[1].text.strip()

        # IP
        ip = proxies[index].select('td')[0].text.strip()

        # Proxy set
        proxies_url.append(f'{ip}:{port}')
        
    return proxies_url

@retry_with_delay(retry_count=RETRY_COUNT, delay_seconds=DELAY_SECONDS, verbose=VERBOSE, verbose_period=VERBOSE_PERIOD)
def _get_proxies_2(verify: bool = True):
    """
    `https://proxyscrape.com/free-proxy-list?ref=ymmxztq&tm_subid1=free-proxy-server-list`로부터 프록시서버 URL을 가져온다.
    
    **참조**
    1. https://www.guru99.com/ko/free-proxy-server-list.html

    Args:
        verify (bool, optional): HTTPS 요청을 보낼 때 서버의 SSL 인증서를 검증할지 여부. default=True.
    
    Returns:
        list[str]: 프록시서버 URL로 이루어진 리스트.
    """


    url = 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text'
    response = requests.get(url, verify=verify)
    proxies = response.text.split('\r\n')
    return proxies

def get_proxies(verify: bool = True):
    """
    프록시 서버를 URL을 가져온다.
    
    Args:
        verify (bool, optional): HTTPS 요청을 보낼 때 서버의 SSL 인증서를 검증할지 여부. default=True.
    
    Returns:
        list[str]: 프록시서버 URL로 이루어진 리스트.
    """

    # get proxies
    proxies_1 = _get_proxies_1(verify)
    proxies_2 = _get_proxies_2(verify)
    proxies = proxies_1 + proxies_2

    # shuffle
    random.shuffle(proxies)

    return proxies

# import requests
# from bs4 import BeautifulSoup
# from tqdm import trange
# from joblib import Parallel, delayed
# import numpy as np
# import pandas as pd

# URL_FORMAT = 'https://iproyal.com/free-proxy-list/?page={}&entries=100'
# SELECTOR_LASTPAGE = r'body > main > section.content-sizer.max-sm\:pr-0.astro-lmapxigl.gap-y-32.sm\:gap-y-40.lg\:gap-y-56.astro-56e3j7ak > div.flex.rounded-8.max-sm\:pr-16.flex-col.max-md\:gap-24.gap-16.max-md\:justify-start.items-center.lg\:flex-row.justify-end.mt-16.md\:mt-24.astro-lmapxigl > div > ul > li:nth-child(8) > a > span'
# SELECTOR_PROXIES = r'body > main > section.content-sizer.max-sm\:pr-0.astro-lmapxigl.gap-y-32.sm\:gap-y-40.lg\:gap-y-56.astro-56e3j7ak > div.max-sm\:overflow-auto.max-md\:pr-16.astro-lmapxigl > div > div:nth-child({}) > div:nth-child({})'

# def get_iproyal_proxies_by_page(page):
#     response = requests.get(URL_FORMAT.format(page))
#     proxies_info = []
#     if response.status_code==200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         for i in range(100):
#             try:
#                 proxy_info = [soup.select_one(SELECTOR_PROXIES.format(i+2,j+1)).text for j in range(3)] # ip, port, protocol
#                 proxies_info.append(proxy_info)
#             except:
#                 break
#     return proxies_info

# # 마지막 페이지 가져오기
# response = requests.get(URL_FORMAT.format(1))
# soup = BeautifulSoup(response.text, 'html.parser')
# lastpage = int(soup.select_one(SELECTOR_LASTPAGE).text)

# proxies_info = Parallel(n_jobs=os.cpu_count())(
#     delayed(get_iproyal_proxies_by_page)(i+1) for i in trange(lastpage)
# )
# proxies_info = np.vstack(proxies_info)
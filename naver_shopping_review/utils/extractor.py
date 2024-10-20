"""
네이버쇼핑 리뷰데이터 수집과 관련하여, extractor 관련 클래스를 제공한다.

클래스 목록
1. `NaverShoppingExtractor`
    네이버쇼핑에서 키워드를 검색했을 때 나오는 네이버페이 정보를 API를 통해 크롤링하는 클래스. lib.python.crawler.BaseExtractor를 상속받아 만들어진다.
2. `NaverShoppingReviewExtractor`
    네이버쇼핑에서 네이버페이 상품페이지의 리뷰에 대한 정보를 API를 통해 크롤링하는 클래스. lib.python.crawler.BaseExtractor를 상속받아 만들어진다.
"""

# lib
from lib.python.crawl import BaseExtractor
from lib.python.decorators import retry_with_delay

# crawling
from crawling.naver_shopping_review.utils import add_headers_randomly, get_proxies

# default
import json
import random
import requests
import urllib
from fake_useragent import UserAgent

# global setting
RETRY_COUNT = -1
DELAY_SECONDS = (0.1,0.3)
VERBOSE = 0
VERBOSE_PERIOD = 1

UA = UserAgent()

class NaverShoppingExtractor(BaseExtractor):
    """네이버쇼핑에서 키워드를 검색했을 때 나오는 네이버페이 정보를 API를 통해 크롤링하는 클래스. lib.python.crawler.BaseExtractor를 상속받아 만들어진다."""
    
    def __init__(self):
        """NaverShoppingExtractor의 생성자로, lib.python.crawler.BaseExtractor를 상속받아 만들어진다."""
        
        self.proxies_list = get_proxies(verify=True)
    
    @retry_with_delay(retry_count=RETRY_COUNT, delay_seconds=DELAY_SECONDS, verbose=VERBOSE, verbose_period=VERBOSE_PERIOD)
    def crawl(self, keyword: str, page: str|int) -> json:
        """
        Queue에 들어온 메시지를 기반으로 크롤링을 진행하는 함수로, extractor의 진입함수.
        
        Args:
            keyword (str): 수집을 원하는 키워드명.
            page (str|int): 수집을 원하는 페이지.
            
        Returns:
            json: 수집 API로부터 전달받은 Parsing된 결과 데이터.
        """
        
        return self.request(keyword, page)
    
    def request(self, keyword: str, page: str|int) -> json:
        """
        수집 API에 크롤링 요청을 보내는 함수.
        
        Args:
            keyword (str): 수집을 원하는 키워드명.
            page (str|int): 수집을 원하는 페이지.
            
        Returns:
            json: 수집 API로부터 전달받은 Parsing된 결과 데이터.
        """
        
        # get proxies
        if len(self.proxies_list)==0:
            self.proxies_list = get_proxies(verify=True)
        
        url = 'https://search.shopping.naver.com/search/all'

        cookies = {
            'NNB': 'FQTBKMTQEV3WG',
            'NID_AUT': 'gvJsXPhQYqbFr2Pq0LzEnlIkcpV/4DvZ2Nv9xVUdBlQUljF6/sFp4YxHEfgSTiYB',
            'NID_JKL': 'eyNNuWCuSajGhKc58q5w9Eb0cZRvI9BY0JXFrH65O4A=',
            'NAC': 'EzcXBMgVB4leB',
            'ASID': '1b2313bc000001903bd7270000000043',
            'SHP_BUCKET_ID': '1',
            'spage_uid': '',
            'NID_SES': 'AAABrfWOhcv9S1022b1lNHa69zvAlKYeyl2JkpcjFNsRQE+ARI9uZgBlxBlCrLDooL0W9S6U75gYYgX1xhozXZsuUKo2wzTnmT8iVrYDTVSOMFQjAQzOZlc4HF9mbnrTpBt94ljBdL4JBihFCcAXyZzBuFjlD9xOY3/lHqlsu1C7Wf8gXjgKDpV1dHYO2WXyd9oH6yJuQCWh+XInbG81sWOBZStzghKzPeP6ryp1BqxtN27lg8baiDyk5rVvP5JxOKDrZNkLGMvhg4gGOwc3pR+6W4WhBA6w6BsYKdk/JCxt4AHm0J8GLt14W8OR8qKdDFPycamIis9onqXfpKEAmmhS/N30Iw9sTlH3ShHP4c73mGsvt2uuGQj0USgZGHxiQlmDTL81g9VcZnh3wyFVjEg5ITEGWB7ZXplGAGA98fyFIRs3D4cBgG5kd+DVgCC5CW3gSy4Z13lf49J66j7UxZ59qukun7ven2nmnPwV4DgXtxy05sh59kHaLqEGOvEJjzjfxG0/qEj8jhsDODvJ/jA+D9AaTokaIgn45t13K+YEz5UezbgFsQZjsMWZ8XvxHgDeyQ==',
            'ncpa': '701151|lxyyjyc8|6a313a2c31ab6fd18377ff9ab24deb6c99117292|s_f0de38c92f99|88e42eaa26504f30064bbe068639fff37bbb5ce8:849040|lxyym49s|eb371934ddc9838867ecfd28f01a59dc397cfaa8|s_23a46a96bc6f1|3301a48a00e8c859583a5f7317cea8acfd0b2244:425796|lxz63iko|46e9c2c1311ee50011db18c9b937f2921e83f44c|s_591787468346782261|c01c3f49c9b44df468cfe8ea4272d48e14827c6b:3316929|lxz6g5tk|d7cdbf7a890101b8c0e465c3e0601dbb2aa5bd40|s_25d12ee472e4|fe16356a046bf6fa0e83c918e91711e9ef359f6e:5278144|lxz705q8|61178200b73d1faa4c99d1b1dbb47f34fe5a6056|s_1094171d5a3ed|4332edf748139d2f24fe6ca43767261e23cc3a62',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://shopping.naver.com/home',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.127", "Google Chrome";v="126.0.6478.127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': str(UA.random),
        }

        params = {
            'adQuery': keyword,
            'origQuery': keyword,
            'pagingIndex': str(page),
            'pagingSize': '40',
            'productSet': 'checkout', # 네이버페이 상품
            'query': keyword,
            'sort': 'rel',
            'timestamp': '',
            'viewType': 'list',
        }

        # request
        idx = random.choice(range(len(self.proxies_list)))
        proxies = self.proxies_list[idx]
        response = requests.get(url, headers=headers, params=params, cookies=cookies, proxies={'http':'http://'+proxies})
        
        # check request
        if response.status_code!=200:
            self.proxies_list.pop(idx)
            raise ConnectionError(f"[{response.status_code}] IP has been blocked (ip={proxies}, remaining={len(self.proxies_list)})")
        
        return response
        
class NaverShoppingReviewExtractor(BaseExtractor):
    """네이버쇼핑에서 네이버페이 상품페이지의 리뷰에 대한 정보를 API를 통해 크롤링하는 클래스. lib.python.crawler.BaseExtractor를 상속받아 만들어진다."""
    
    def __init__(self, verbose: bool = True):
        """
        NaverShoppingReviewExtractor의 생성자로, lib.python.crawler.BaseExtractor를 상속받아 만들어진다.
        
        Args:
            verbose (bool, optional): IP차단 발생 시 에러 텍스트를 출력할지 여부. default=True.
        """
        
        self.verbose = verbose
        self.proxies_list = get_proxies(verify=True)
    
    @retry_with_delay(retry_count=RETRY_COUNT, delay_seconds=DELAY_SECONDS, verbose=VERBOSE, verbose_period=VERBOSE_PERIOD)
    def crawl(self, merchant_no: str|int, mall_product_no: str|int, org_mall_product_no: str|int, mall_pc_url: str, page: str|int) -> json:
        """
        Queue에 들어온 메시지를 기반으로 크롤링을 진행하는 함수로, extractor의 진입함수.
        
        Args:
            merchant_no (str|int): 수집을 원하는 상품의 merchant no.
            mall_product_no (str|int): 수집을 원하는 상품의 mall product no.
            org_mall_product_no (str|int): 수집을 원하는 상품의 original mall product no.
            mall_pc_url (str): 수집을 원하는 상품의 mall pc url.
            page (str|int): 수집을 원하는 리뷰페이지.
            
        Returns:
            json: 수집 API로부터 전달받은 Parsing된 결과 데이터.
        """
        
        return self.request(merchant_no, mall_product_no, org_mall_product_no, mall_pc_url, page)
    
    def request(self, merchant_no: str|int, mall_product_no: str|int, org_mall_product_no: str|int, mall_pc_url: str, page: str|int) -> json:
        """
        수집 API에 크롤링 요청을 보내는 함수.
        
        Args:
            merchant_no (str|int): 수집을 원하는 상품의 merchant no.
            mall_product_no (str|int): 수집을 원하는 상품의 mall product no.
            mall_product_no (str|int): 수집을 원하는 상품의 original mall product no.
            mall_pc_url (str): 수집을 원하는 상품의 mall pc url.
            page (str|int): 수집을 원하는 리뷰페이지.
            
        Returns:
            json: 수집 API로부터 전달받은 Parsing된 결과 데이터.
        """

        assert page<=1000, "maximum page is 1000."
        
        # get proxies
        if len(self.proxies_list)==0:
            self.proxies_list = get_proxies(verify=True)
        
        url = 'https://smartstore.naver.com/i/v1/contents/reviews/query-pages'
        referer = f'{mall_pc_url}/products/{mall_product_no}'

        cookies = {
            'NNB': 'FQTBKMTQEV3WG',
            'NID_AUT': 'gvJsXPhQYqbFr2Pq0LzEnlIkcpV/4DvZ2Nv9xVUdBlQUljF6/sFp4YxHEfgSTiYB',
            'NID_JKL': 'eyNNuWCuSajGhKc58q5w9Eb0cZRvI9BY0JXFrH65O4A=',
            'NAC': 'EzcXBMgVB4leB',
            'ASID': '1b2313bc000001903bd7270000000043',
            'NACT': '1',
            'CRF_TOOLTIP': 'true',
            'NID_SES': 'AAABrfWOhcv9S1022b1lNHa69zvAlKYeyl2JkpcjFNsRQE+ARI9uZgBlxBlCrLDooL0W9S6U75gYYgX1xhozXZsuUKo2wzTnmT8iVrYDTVSOMFQjAQzOZlc4HF9mbnrTpBt94ljBdL4JBihFCcAXyZzBuFjlD9xOY3/lHqlsu1C7Wf8gXjgKDpV1dHYO2WXyd9oH6yJuQCWh+XInbG81sWOBZStzghKzPeP6ryp1BqxtN27lg8baiDyk5rVvP5JxOKDrZNkLGMvhg4gGOwc3pR+6W4WhBA6w6BsYKdk/JCxt4AHm0J8GLt14W8OR8qKdDFPycamIis9onqXfpKEAmmhS/N30Iw9sTlH3ShHP4c73mGsvt2uuGQj0USgZGHxiQlmDTL81g9VcZnh3wyFVjEg5ITEGWB7ZXplGAGA98fyFIRs3D4cBgG5kd+DVgCC5CW3gSy4Z13lf49J66j7UxZ59qukun7ven2nmnPwV4DgXtxy05sh59kHaLqEGOvEJjzjfxG0/qEj8jhsDODvJ/jA+D9AaTokaIgn45t13K+YEz5UezbgFsQZjsMWZ8XvxHgDeyQ==',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://smartstore.naver.com',
            'priority': 'u=1, i',
            'referer' : referer,
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(UA.random),
            'x-client-version': '20240626111623',
        }

        json_data = {
            'checkoutMerchantNo': merchant_no,
            'originProductNo': org_mall_product_no,
            'page': str(page),
            'pageSize': 20,
            'reviewSearchSortType': 'REVIEW_RANKING',
        }
        
        # request
        idx = random.choice(range(len(self.proxies_list)))
        proxies = self.proxies_list[idx]
        response = requests.post(url, cookies=cookies, headers=headers, json=json_data, proxies={'http':'http://'+proxies})
        
        # check request
        if response.status_code!=200:
            self.proxies_list.pop(idx)
            raise ConnectionError(f"[{response.status_code}] IP has been blocked (ip={proxies}, remaining={len(self.proxies_list)}, site={referer}")
        
        return response
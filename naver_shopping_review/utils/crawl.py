"""
네이버쇼핑 리뷰데이터 수집과 관련하여, 크롤링에 필요한 함수와 클래스를 제공한다.

함수 목록
1. `product_response_to_data`
    크롤링 해온 상품정보 response를 pd.DataFrame 형태로 변환한다.
2. `get_products_info`
    입력된 키워드에 대해 입력된 페이지수까지 상품정보를 크롤링해온다.
"""

# root경로를 추가
import os, sys
sys.path.append(os.path.abspath(''))

# crawling
from crawling.naver_shopping_review.utils.extractor import NaverShoppingExtractor, NaverShoppingReviewExtractor

# parallel
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# default
from typing import Callable
import requests
from bs4 import BeautifulSoup
import json
import time
import numpy as np
import pandas as pd

# global setting
DELAY_SECONDS = (0.1,0.3)

def product_response_to_data(response: requests.models.Response,
                             page: int|str) -> pd.DataFrame:
    """
    크롤링 해온 상품정보 response를 pd.DataFrame 형태로 변환한다.
    
    Args:
        response (requests.models.Response): 크롤링 response.
        page (int|str): 페이지 정보.
        
    Returns:
        pd.DataFrame: 데이터프레임 형태로 변환된 네이버 상품정보.
    """

    # 바로 json이 안되므로, select로 필요한 부분 가져오기
    soup = BeautifulSoup(response.text, 'html.parser')
    json_data = json.loads(soup.select("script")[-1].contents[0])
    list_data = json_data['props']['pageProps']['initialState']['products']['list']

    # 페이지의 순위에 맞춰서 광고상품 제거하고 가져오기
    rank = 40*(page-1) + 1
    product_data = []
    
    for i, ele in enumerate(list_data):
        ele = ele['item']
        if ele['rank']==rank:
            rank += 1
            for key in ele.keys():
                ele[key] = str(ele[key])
            d = pd.DataFrame(ele, index=[0])
            product_data.append(d)

            # raise
            if len(d)!=1:
                raise ValueError(f'{i}th value is not unique')

    # concat
    product_data = pd.concat(product_data, axis=0).reset_index(drop=True)

    return product_data

def get_products_info(keyword: str,
                      n_page: str|int,
                      trace_func: Callable = print) -> list[str]:
    """
    입력된 키워드에 대해 입력된 페이지수까지 상품정보를 크롤링해온다.
    
    Args:
        keyword (str): 수집을 원하는 키워드명.
        n_page (str|int): 수집을 원하는 페이지 수.
        trace_func (Callable, optional): 진행 경과를 출력 할 함수. default=print.
        
    Returns:
        list[str]: 상품번호로 이루어진 리스트.
    """

    trace_func('')
    trace_func('<네이버쇼핑 네이버페이 상품 크롤링>')
    trace_func('크롤링 시작')
    trace_func('')

    # extractor 정의
    extractor = NaverShoppingExtractor()

    # 크롤링
    data = []
    for page in range(1,n_page+1):
        trace_func(f'[Products] {page}/{n_page}')

        # 네이버쇼핑 extractor를 통해 크롤링해온다.
        response = extractor.crawl(keyword, page)

        # 크롤링해온 response를 pd.DataFrame 형태로 변환한다.
        d = product_response_to_data(response, page)
        data.append(d)

        # random sleep
        time.sleep(np.random.uniform(DELAY_SECONDS[0],DELAY_SECONDS[1]))

    # concat
    data = pd.concat(data, axis=0).reset_index(drop=True)
    data.insert(0, 'keyword', keyword)

    trace_func('')
    trace_func('크롤링 종료')

    return data

def _get_reviews_iter(extractor: NaverShoppingReviewExtractor,
                      iter: int,
                      page: int,
                      merchant_no: str|int,
                      mall_product_no: str|int,
                      org_mall_product_no: str|int,
                      mall_pc_url: str|int,
                      save_path_format: str = 'product{}_page{}.parquet'):
    """
    크롤링 해온 리뷰정보 iteration에 대한 response를 pd.DataFrame 형태로 저장한다.
    
    Args:
        extractor (crawling.naver_shopping_reviw.utils.extractor.NaverShoppingReviewExtractor)
        iter (int): 상품 iteration.
        page (int): 리뷰 페이지.
        merchant_no (str|int): 수집을 원하는 상품의 merchant no.
        mall_product_no (str|int): 수집을 원하는 상품의 mall product no.
        org_mall_product_no (str|int): 수집을 원하는 상품의 original mall product no.
        mall_pc_url (str): 수집을 원하는 상품의 mall pc url.
        save_path_format (str, optional): 리뷰를 저장할 경로에 대한 포맷. default='product{}_page{}.parquet'.

    Returns:
        None.
    """

    # 크롤링
    response = extractor.crawl(merchant_no, mall_product_no, org_mall_product_no, mall_pc_url, page)
    json_data = response.json()

    # dataframe으로 변환 후, str로 변환
    d = pd.DataFrame(json_data['contents'])
    for col in d.columns:
        d[col] = d[col].astype(str)

    # 상품순위, 리뷰순위 추가
    start = (page-1)*20 + 1
    end   = (page-1)*20 + 1 + len(d)
    d.insert(0, 'product_ranking', iter+1)
    d.insert(1, 'review_ranking', np.arange(start,end))

    # 저장
    d.to_parquet(save_path_format.format(iter+1,page))

    # random sleep
    time.sleep(np.random.uniform(DELAY_SECONDS[0],DELAY_SECONDS[1]))


def get_reviews(products_info: pd.DataFrame,
                save_path_format: str = 'product{}_page{}.parquet',
                max_page: int = 1000,
                trace_func: Callable = print,
                max_workers: int = os.cpu_count()//2) -> pd.DataFrame:
    """
    크롤링 해온 리뷰정보 response를 pd.DataFrame 형태로 변환하여 저장한다.
    
    Args:
        products_info (pd.DataFrame): 상품정보.
        save_path_format (str, optional): 리뷰를 저장할 경로에 대한 포맷. default='product{}_page{}.parquet'.
        max_page (int, optional): 리뷰를 가져올 최대 페이지 수로, 1000을 넘길 수 없다. default=1000.
        trace_func (Callable, optional): 진행 경과를 출력 할 함수. default=print.
        max_workers (int, optional): 병렬 처리를 위한 최대 worker의 수. default=os.cpu_count()//2.

    Returns:
        None.
    """

    assert max_page<=1000, "maximum page is 1000."

    trace_func('')
    trace_func('<네이버쇼핑 네이버페이 상품 리뷰 크롤링>')
    trace_func('크롤링 시작')
    trace_func('')

    # 네이버쇼핑 상품정보 전처리
    # (1) 스마트스토어가 아닌 상품은 리뷰를 가져올수없으므로 제거
    products_info['is_smartstore'] = products_info['mallProductUrl'].str.contains('https://smartstore.naver.com/main/products').astype(int)
    products_info = products_info[products_info['is_smartstore']==1].reset_index(drop=True)

    # (2) 리뷰가 0인 상품들 제거
    products_info = products_info[products_info['reviewCount']!='0'].reset_index(drop=True)

    # extractor 정의
    extractor = NaverShoppingReviewExtractor()

    s_total = time.time()
    for iter in range(len(products_info)):
        s_iter = time.time()

        merchant_no = eval(products_info['mallInfoCache'][iter])['npaySellerNo']
        mall_product_no = products_info['mallProductId'][iter]
        org_mall_product_no = products_info['originalMallProductId'][iter]
        mall_pc_url = products_info['mallPcUrl'][iter]

        # 리뷰페이지별 iteration

        # (1) 첫번째 페이지 크롤링 후, 마지막 페이지 탐색
        response = extractor.crawl(merchant_no, mall_product_no, org_mall_product_no, mall_pc_url, page=1)
        json_data = response.json()

        # (2) 두번째 페이지부터 마지막 페이지까지 가져오기
        last_page = min(json_data['totalPages'], 1000) # 최대 1,000페이지까지만 크롤링 가능
        last_page = min(max_page, last_page)

        # 상품별 iteration
        if max_workers==1:
            for page in range(1,last_page+1,1):
                _get_reviews_iter(extractor, iter, page, merchant_no, mall_product_no, org_mall_product_no, mall_pc_url, save_path_format)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        _get_reviews_iter,
                        extractor, iter, page, merchant_no, mall_product_no, org_mall_product_no, mall_pc_url, save_path_format,
                    )
                    for page in range(1,last_page+1,1)
                ]

                # 모든 작업이 완료될 때까지 기다림
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"An error occurred: {e}")

        # progress
        e_iter = time.time()
        elapsed = e_iter - s_iter
        total = e_iter-s_total
        remainings = (len(products_info)-iter-1)*elapsed

        trace_func(f'[Reviews] {iter+1}/{len(products_info)}, {elapsed=:.2f}s, {total=:.2f}s, {remainings=:.2f}s')

    trace_func('')
    trace_func('크롤링 종료')

    return None
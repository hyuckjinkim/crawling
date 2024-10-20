"""
네이버쇼핑 리뷰데이터 수집과 관련하여, 파이프라인 함수와 클래스를 제공한다.

클래스 목록

"""

# root경로를 추가
import os, sys
sys.path.append(os.path.abspath(''))

# lib
from lib.python.log import get_logger

# crawling
from crawling.naver_shopping_review.utils.crawl import get_products_info, get_reviews

# default
import datetime
import logging

# 기본과 라이브러리의 로거를 가져와서 로그 레벨을 재설정
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("seleniumwire").setLevel(logging.WARNING)

class NaverShoppingReviewGetter:
    """네이버쇼핑 리뷰데이터를 수집한다."""
    
    def __init__(self, keyword: str, n_page: int, max_review_page: int = 100, max_workers: int = os.cpu_count()//2) -> None:
        """
        NaverShoppingReviewGetter의 생성자.
        
        Args:
            keyword (str): 수집 대상 키워드.
            n_page (int): 수집 대상 페이지수.
            max_review_page (int, optional): 리뷰를 가져올 최대 페이지 수로, 1000을 넘길 수 없다. default=100.
            max_workers (int, optional): 병렬 처리를 위한 최대 worker의 수. default=os.cpu_count()//2.
        """
        
        assert max_review_page<=1000, "maximum review page is 1000."

        self.keyword = keyword
        self.n_page = n_page
        self.max_review_page = max_review_page
        self.max_workers = max_workers

        self.start_datetime = datetime.datetime.now()

        # 실행일자, 실행시간
        nowdate = str(self.start_datetime)[:10].replace('-','')

        # 로그 저장경로
        self.log_path = f'.logs/crawling_naver_review_{nowdate}_{keyword}_{n_page}_{max_review_page}.log'
        self.logger = get_logger(save_path=self.log_path)
        self.trace_func = self.logger.info

        # 리뷰 저장경로
        self.save_dir = f'crawling/naver_shopping_review/.result/{nowdate}_{keyword}_{n_page}_{max_review_page}/'
        os.system(f'rm -rf {self.save_dir}')

        self.product_save_path_format = self.save_dir + 'product_page{}.parquet'
        self.review_save_path_format = self.save_dir + 'review_product{}_page{}.parquet'
        os.makedirs(self.save_dir, exist_ok=True)

    def run(self):
        # 상품정보 수집
        products_info = get_products_info(self.keyword, self.n_page, self.trace_func)
        products_info.to_parquet(self.product_save_path_format.format(self.n_page))

        # 리뷰정보 수집
        get_reviews(products_info, self.review_save_path_format, self.max_review_page, self.trace_func, self.max_workers)

        end_datetime = datetime.datetime.now()
        run_time = (end_datetime - self.start_datetime).seconds / 60

        self.trace_func(f'[실행시간] {self.start_datetime}')
        self.trace_func(f'[종료시간] {end_datetime}')
        self.trace_func(f'[실행시간] {run_time:.2f} min')
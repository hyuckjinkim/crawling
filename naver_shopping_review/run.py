# root경로를 추가
import os, sys
sys.path.append(os.path.abspath(''))

# crawling
from crawling.naver_shopping_review.pipeline import NaverShoppingReviewGetter

# default
import argparse

# set the argument parser
parser = argparse.ArgumentParser(description="Naver Shopping Review Crawling")
parser.add_argument('--keywords', type=str, help="크롤링을 원하는 키워드명을 입력하세요. 키워드가 여러개라면 ','로 나눠서 입력하세요.")
parser.add_argument('--n_page', type=int, default=1, help="크롤링을 원하는 상품의 페이지 수를 입력하세요.")
parser.add_argument('--max_review_page', type=int, default=1, help="크롤링을 원하는 리뷰의 최대 페이지 수를 입력하세요.")
parser.add_argument('--max_workers', type=int, default=os.cpu_count()//2, help="병렬 처리를 위한 최대 worker의 개수를 입력하세요.")

# get argument from argment parset
args = parser.parse_args()
keywords = args.keywords
n_page = args.n_page
max_review_page = args.max_review_page
max_workers = args.max_workers

# run
if __name__=='__main__':
    keywords = keywords.replace(' ','').split(',')
    for i, keyword in enumerate(keywords):
        getter = NaverShoppingReviewGetter(keyword, n_page, max_review_page, max_workers)
        getter.trace_func(f'[{str(i+1).zfill(len(str(len(keywords))))}/{len(keywords)}] {keyword}')
        getter.run()
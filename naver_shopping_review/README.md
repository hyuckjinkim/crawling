# 네이버쇼핑 리뷰데이터 수집
네이버쇼핑에서 선택한 키워드의 순위별로 상품리뷰를 수집한다.
마지막 수정일자 : 2024-07-01.
네이버쇼핑플러스로 개편됨에 따라, 코드 사용이 불가능해졌습니다.

## 실행 : git bash에서 작업
```
# crawl 가상환경 실행
conda activate crawl

# nohub  (pid: 666)
# 상품당 최대 20 x 100 = 2,000개 리뷰
# 전체상품 200 x 2000 = 400,000개 리뷰
nohup python crawling/naver_shopping_review/run.py\
    --keyword '오메가3,밀크씨슬,마그네슘'\
    --n_page 5\
    --max_review_page 100\
    --max_workers 12\
    > .logs/nohup.out 2>&1 < /dev/null &

# check
tail -f .logs/nohup.out
```
# dna-data

poetry 설치 방법

 - poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

 - poetry shell 설치
poetry self add poetry-plugin-shell

 - poetry shell 활성화
poetry shell

 - 추가된 패키지 설치하기
poetry install

 - 프리커밋 활성화
pre-commit install

# Alembic을 MySQL 데이터베이스와 함께 사용 설정하기

 - mysql 켜기
sudo mysql -u root

 - db 만들기 (권한이 없기 때문에 반듯이 만들어 줘야함!)
CREATE DATABASE test_db_2;

 - 비밀 번호 설정 .env에 아래와 같이 추가하기
DATABASE_USERNAME = "root"
DATABASE_PASSWORD = "pass"

 - db 생성
alembic upgrade head

 - 아래 코드로 생성된 테이블을 확인 하는 것도 가능!
USE DATABASE test_db_2;
SHOW TABLES

# uvicorn 실행
nohup uvicorn main:app --host 0.0.0.0 --port 5173 --reload > uvicorn.log 2>&1 &
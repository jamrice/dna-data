# dna-data

# Alembic을 MySQL 데이터베이스와 함께 사용 설정하기

## 필수 사항

Alembic을 설정하기 전에 다음 항목들이 준비되어 있는지 확인하세요:

- Python 3.x
- Alembic 설치
- MySQL 서버가 실행 중이고 접근 가능한 상태

### 1. Alembic과 MySQL Connector 설치

먼저 Alembic과 MySQL 커넥터(`mysql-connector-python`)를 설치합니다. 다음 명령어를 실행하세요:

```bash
pip install alembic
pip install mysql-connector-python
```

### 2. Alembic 초기화

프로젝트 디렉토리에서 아래 명령어를 실행하여 Alembic을 초기화합니다. 이 명령어는 `alembic.ini` 설정 파일과 필요한 폴더 구조를 생성합니다.

```bash
alembic init alembic
```

### 3. `alembic.ini` 파일 설정

Alembic이 초기화되면 프로젝트 디렉토리 내에 `alembic.ini` 파일이 생성됩니다. 이 파일을 열고 `sqlalchemy.url` 설정 항목을 찾습니다. 이 항목은 Alembic이 마이그레이션을 실행할 때 사용할 데이터베이스 연결 URL을 정의합니다.

다음과 같은 형식으로 `sqlalchemy.url`을 업데이트하세요:

```ini
sqlalchemy.url = mysql+mysqlconnector://username:password@localhost/db_name
```

- `username`을 MySQL 데이터베이스의 사용자 이름으로 바꿉니다.
- `password`를 MySQL 데이터베이스의 비밀번호로 바꿉니다.
- `localhost`를 MySQL 서버의 주소로 바꿉니다 (로컬 머신이 아닌 경우).
- `db_name`을 사용하려는 MySQL 데이터베이스의 이름으로 바꿉니다.

예를 들어, MySQL 사용자 이름이 `root`, 비밀번호가 `password123`, 데이터베이스 이름이 `mydatabase`인 경우, 설정은 다음과 같이 변경됩니다:

```ini
sqlalchemy.url = mysql+mysqlconnector://root:password123@localhost/mydatabase
```

### 4. Alembic 마이그레이션 실행하기

데이터베이스 URL을 설정한 후에는 Alembic을 사용하여 마이그레이션을 실행할 수 있습니다. 새 마이그레이션 파일을 생성하려면 다음 명령어를 실행하세요:

```bash
alembic revision --autogenerate -m "migration message"
```

마이그레이션을 데이터베이스에 적용하려면 아래 명령어를 실행하세요:

```bash
alembic upgrade head
```

### 5. 문제 해결

- MySQL 서버가 실행 중이고, 제공된 사용자 이름과 비밀번호가 정확한지 확인하세요.
- `alembic`과 `mysql-connector-python` 패키지가 올바르게 설치되었는지 확인하세요.
- `alembic.ini` 파일 내 `sqlalchemy.url` 항목에 오타가 없는지 다시 확인하세요.

---

이 README 파일은 Alembic을 설정하고 MySQL 데이터베이스와 연결하는 방법을 안내합니다. `alembic.ini` 파일에서 MySQL 연결 정보를 정확히 입력하고, 이후 Alembic을 사용하여 데이터베이스 마이그레이션을 진행할 수 있습니다.
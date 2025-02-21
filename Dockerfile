# 가벼운 이미지 사용
FROM python:3.10-slim  

WORKDIR /app

# 패키지 리스트 먼저 복사 → 캐시 최적화
COPY requirements.txt .

# 필요한 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 코드 복사
COPY . .

# 컨테이너 실행 명령어
CMD ["python", "src/load.py"]

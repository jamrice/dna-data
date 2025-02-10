import logging
import os
from datetime import datetime

now = datetime.now()
formatted_time = now.strftime("%Y%m%d%H%M")
# 로그 저장 경로 설정
log_file_path = os.path.join(os.getcwd(), "./logs/" + formatted_time + ".log")

# 로거(Logger) 생성
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)  # 가장 상세한 수준인 DEBUG 레벨 설정

# 파일 핸들러 생성
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 콘솔에 로그를 출력하기 위한 핸들러(Handler) 생성
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 콘솔에는 DEBUG 이상 레벨만 출력

# 로그 포맷(Formatter) 설정
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)
# 로거에 핸들러 추가
logger.addHandler(console_handler)
logger.addHandler(file_handler)

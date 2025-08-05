# backend/Dockerfile (Python 3.12)
FROM python:3.12-slim
WORKDIR /app

# 시스템 종속성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 프로젝트 파일 복사
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 전체 복사
COPY . .

# FastAPI + Uvicorn 실행 (main.py에 FastAPI 객체가 app으로 정의되어 있다고 가정)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.10.1
WORKDIR /usr/src/app
COPY requirements.txt ./requirements.txt
COPY src ./src
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--root-path", "$API_ROOT_PATH"]
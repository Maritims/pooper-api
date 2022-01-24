FROM python:3.10.1
WORKDIR /usr/src/app
ENV VIRTUAL_ENV=venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt ./requirements.txt
COPY src ./src
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
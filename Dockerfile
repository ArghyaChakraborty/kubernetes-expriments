FROM python:3.5.3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY operator.py ./

CMD [ "python", "--version" ]

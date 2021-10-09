FROM python:3

WORKDIR /mitmproxy
COPY . /mitmproxy

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8080
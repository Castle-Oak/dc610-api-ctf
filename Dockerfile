FROM ubuntu:22.04

# MAINTANER Your Name "youremail@domain.tld"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-venv

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python3 -m venv /venv
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "uvicorn" ]

CMD [ "app:app", "--host", "0.0.0.0", "--port", "80" ]
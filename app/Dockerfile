# start from base

FROM ubuntu:20.04
LABEL maintainer="Ivan Dallaserra <ivandal77@gmail.com>"
RUN apt-get update -y && \
apt-get install -y python3-pip python3-dev libmariadb-dev
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app
CMD [ "python3", "./app.py" ]

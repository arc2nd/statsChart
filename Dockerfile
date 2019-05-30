# start with ubuntu
FROM python:3.6-slim

# copy over our requirements file
COPY requirements.txt /tmp/

COPY . /srv/webapp
WORKDIR /srv/webapp

# update and install some stuff
RUN apt-get clean && apt-get -y update 
RUN apt-get install -y nginx python3-dev python-pip python-dev build-essential
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

COPY nginx.conf /etc/nginx/nginx.conf
RUN chmod +x ./start.sh
CMD ["./start.sh"]

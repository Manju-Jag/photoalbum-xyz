FROM ubuntu

RUN sudo apt-get update
RUN sudo apt-get install -y python3
RUN sudo apt-get install -y python3-pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY photoalbum.py .
COPY config.py .
ENTRYPOINT FLASK_APP=photoalbum.py flask run  --host 0.0.0.0

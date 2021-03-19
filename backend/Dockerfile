FROM python:3.8-slim

COPY . /geez/
WORKDIR /geez

# Debugging
RUN apt-get update && apt-get install -y vim procps

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN chmod +x geez/main.py
ENTRYPOINT [ "python3", "geez/main.py" ]

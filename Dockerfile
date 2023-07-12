FROM python:3.11
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY app /code/app
COPY app/db /code/app/db
CMD ["/bin/bash", "-c","cd /code/app; python3 /code/app/main.py & python3 /code/app/modelthreads2.py"]
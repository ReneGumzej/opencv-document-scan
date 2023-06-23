FROM python:3.11

ADD main.py .

COPY requirements.txt . 
RUN apt-get update && apt-get install -y libgl1
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./main.py"]
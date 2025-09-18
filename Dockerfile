FROM python:3.10-alpine

WORKDIR /app

ADD ./requirements.txt /app/
ADD ./workoutsync /app/workoutsync
RUN pip --no-cache-dir install -r requirements.txt

ENTRYPOINT ["python", "-m"]
CMD []

<<<<<<< HEAD
FROM alpine:3.4
RUN apk add --update python3
ADD ./app /Racecontrol_bot/
WORKDIR /Racecontrol_bot/
RUN mkdir tmp/
RUN pip3 install --no-cache-dir -r requirements.txt
ENV TOKEN ''
CMD python3 core.py
=======
FROM alpine:latest
COPY ./app /Racecontrol_bot/
WORKDIR /Racecontrol_bot/
RUN apk add --no-cache python3 \
  && mkdir tmp/ \
  && pip3 install --upgrade pip \
  && pip3 install --no-cache-dir -r requirements.txt
ENV TOKEN ''
ENV TIME="-1"
CMD python3 -u core.py
>>>>>>> service

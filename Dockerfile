FROM alpine:latest
RUN apk add --update python3
ADD ./app /Racecontrol_bot/
WORKDIR /Racecontrol_bot/
RUN mkdir tmp/
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
ENV TOKEN ''
ENV TIME="-1"
CMD python3 -u core.py
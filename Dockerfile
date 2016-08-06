FROM alpine:3.4
RUN apk add --update python3
ADD ./app /Racecontrol_bot/
WORKDIR /Racecontrol_bot/
RUN mkdir tmp/
RUN pip3 install --no-cache-dir -r requirements.txt
ENV TOKEN ''
CMD python3 core.py
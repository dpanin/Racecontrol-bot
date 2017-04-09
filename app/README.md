# Racecontrol bot for Telegram
This bot gets new messages from racecontrol.me and posts them to Telegram channel.
# Install
Pull from Docker Hub:
```
docker pull boomyr/vk_bot
```
Run the container with your bot token and timestamp:
```
docker run -d -e "TOKEN=your_token" -e "TIME=your_time" rc-bot
```
Note: if you don’t set your TIME variable, news will start fetching from present time.
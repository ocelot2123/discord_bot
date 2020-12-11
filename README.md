# Among Us Discord Bot
Discord chatbot for scheduling Among Us game sessions

## Quick start
Install with:
```
pip install -r requirements.txt
```
To run:
```
python3 main.py
```
or alternatively run with screen:
```
screen -L python3 main.py
```

## Main Commands

```
!play [time (default = 21:00)] = starts a queue for [time]
!imsus [name(optional)] = adds you to an existing queue with optional name (or for signing up for other people)
!imnotsus [name(optional)] = removes you from the queue
!changetime [time] = changes game time to [time]
!session = resends current session info
!reset = empties queue
!mapvote = start a poll for map selection, !endvote to end the vote
!skeld = brings up an image of the map skeld
!mirahq = brings up an image of the map mirahq
!polus = brings up an image of the map polus
```

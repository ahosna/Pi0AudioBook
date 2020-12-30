from gpiozero import Button
from time import sleep
from mpd import MPDClient
from contextlib import contextmanager
import os

DATA_DIR="/data"

BTN_PLAY=10
BTN_PREV=9
BTN_NEXT=11

BOUNCE_TIME=None
HOLD_TIME=1.0

RADIOS=[
    "http://live.slovakradio.sk:8000/Slovensko_128.mp3",
    "http://live.slovakradio.sk:8000/Litera_128.mp3",
]

held_btn_play = False
held_btn_prev = False
held_btn_next = False
is_radio_mode = False
song_position = 0
radio_position = 0

client = MPDClient()

@contextmanager
def mpd_client():
    global client
    try:
        client.connect("127.0.0.1", 6600)
        yield client
    finally:
        client.close()
        client.disconnect()

def prev_held():
    global held_btn_prev
    print("<< held")
    if is_radio_mode:
        return 
    with mpd_client() as mpd:
        mpd.play(0)
    held_btn_prev = True

def next_held():
    global held_btn_next
    print(">> held")
    if is_radio_mode:
        return 
    with mpd_client() as mpd:
        status = mpd.status()
        pos = int(status["song"]) + 10
        if pos > int(status["playlistlength"]): 
            pos = 0
        mpd.play(pos)
    held_btn_next = True

def play_held(btn):
    global held_btn_play
    global is_radio_mode
    global song_position
    print("|| held")
    if is_radio_mode:
        # switch to player mode
        is_radio_mode=False
        setup_player(song_position)
    else:
        with mpd_client() as mpd:
            status = mpd.status()
            song_position = int(status["song"])
        #switch to radio mode
        is_radio_mode=True
        setup_radio(0)

    held_btn_play = True

def prev_released():
    global held_btn_prev
    if not held_btn_prev:
        print("<< released")
        if is_radio_mode:
            return 
        with mpd_client() as mpd:
            mpd.previous()
    held_btn_prev = False

def next_released():
    global held_btn_next
    if not held_btn_next:
        print(">> released")
        with mpd_client() as mpd:
            if is_radio_mode:
                radio_position = (radio_position + 1) % len(RADIOS)
                setup_radio(radio_position)
            else:
                mpd.next()
    held_btn_next = False

def play_released():
    global held_btn_play
    if not held_btn_play:
        print("|| released")
        with mpd_client() as mpd:
            mpd.pause()
    held_btn_play = False

def setup_buttons():
    global btn_next
    global btn_prev
    global btn_play
    btn_next = Button(BTN_NEXT, bounce_time=BOUNCE_TIME, hold_time=HOLD_TIME)
    btn_next.when_released = next_released
    btn_next.when_held = next_held

    btn_prev = Button(BTN_PREV, bounce_time=BOUNCE_TIME, hold_time=HOLD_TIME)
    btn_prev.when_released = prev_released
    btn_prev.when_held = prev_held

    btn_play = Button(BTN_PLAY, bounce_time=BOUNCE_TIME, hold_time=HOLD_TIME)
    btn_play.when_released = play_released
    btn_play.when_held = play_held

def setup_player(song_position=0):
    with mpd_client() as mpd:
        mpd.update()
        mpd.repeat(1)
        mpd.single(0)
        mpd.clear()
        files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".mp3"))
        for f in files:
            mpd.add(f)
        mpd.play(song_position)

def setup_radio(radio_position=0):
    with mpd_client() as mpd:
        mpd.clear()
        mpd.add(RADIOS[radio_position])
        mpd.play()

setup_buttons()
setup_radio(radio_position)

while(True):
    sleep(1)

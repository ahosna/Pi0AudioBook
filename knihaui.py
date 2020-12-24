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

held_btn_play = False
held_btn_prev = False
held_btn_next = False

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
    with mpd_client() as mpd:
        mpd.play(0)
    held_btn_prev = True

def next_held():
    global held_btn_next
    print(">> held")
    with mpd_client() as mpd:
        status = mpd.status()
        pos = int(status["song"]) + 10
        if pos > int(status["playlistlength"]): 
            pos = 0
        mpd.play(pos)
    held_btn_next = True

def play_held(btn):
    global held_btn_play
    print("|| held")
    held_btn_play = True

def prev_released():
    global held_btn_prev
    if not held_btn_prev:
        print("<< released")
        with mpd_client() as mpd:
            mpd.previous()
    held_btn_prev = False

def next_released():
    global held_btn_next
    if not held_btn_next:
        print(">> released")
        with mpd_client() as mpd:
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

def setup_client():
    with mpd_client() as mpd:
        mpd.update()
        mpd.repeat(1)
        mpd.single(0)
        mpd.clear()
        files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".mp3"))
        for f in files:
            mpd.add(f)
        mpd.play(0)

setup_buttons()
setup_client()

while(True):
    sleep(1)

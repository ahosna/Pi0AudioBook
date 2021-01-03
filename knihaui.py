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


class State:
    held_btn_play= False
    held_btn_prev= False
    held_btn_next= False
    is_radio_mode= True
    song_position = 0
    radio_position = 0

state = State()

@contextmanager
def mpd_client():
    global state
    try:
        client = MPDClient()
        client.connect("127.0.0.1", 6600)
        yield client
    finally:
        client.close()
        client.disconnect()

def prev_held():
    global state
    print("<< held")
    if state.is_radio_mode:
        return 
    with mpd_client() as mpd:
        mpd.play(0)
    state.held_btn_prev = True

def next_held():
    global state
    print(">> held")
    if state.is_radio_mode:
        return 
    with mpd_client() as mpd:
        status = mpd.status()
        pos = int(status["song"]) + 10
        if pos > int(status["playlistlength"]): 
            pos = 0
        mpd.play(pos)
    state.held_btn_next = True

def play_held(btn):
    global state
    print("|| held")
    if state.is_radio_mode:
        # switch to player mode
        state.is_radio_mode=False
        setup_player(state.song_position)
    else:
        #switch to radio mode
        with mpd_client() as mpd:
            status = mpd.status()
            state.song_position = int(status["song"])
        state.is_radio_mode=True
        setup_radio(0)

    state.held_btn_play = True

def prev_released():
    global state
    if not state.held_btn_prev:
        print("<< released")
        if state.is_radio_mode:
            state.radio_position -= 1
            if state.radio_position < 0:
                state.radio_position = len(RADIOS)-1
            setup_radio(state.radio_position)
            return 
        with mpd_client() as mpd:
            mpd.previous()
    state.held_btn_prev = False

def next_released():
    global state
    if not state.held_btn_next:
        print(">> released")
        if state.is_radio_mode:
            state.radio_position = (state.radio_position + 1) % len(RADIOS)
            setup_radio(state.radio_position)
        else:
            with mpd_client() as mpd:
                mpd.next()
    state.held_btn_next = False

def play_released():
    global state
    if not state.held_btn_play:
        print("|| released")
        with mpd_client() as mpd:
            mpd.pause()
    state.held_btn_play = False

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
    global state
    with mpd_client() as mpd:
        mpd.update()
        mpd.repeat(1)
        mpd.single(0)
        mpd.clear()
        files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".mp3"))
        for f in files:
            print(f)
            mpd.add(f)
        mpd.play(song_position)
    state.song_position = song_position

def setup_radio(radio_position=0):
    global state
    with mpd_client() as mpd:
        mpd.clear()
        mpd.add(RADIOS[radio_position])
        mpd.play(0)
    state.radio_position = radio_position

setup_buttons()
setup_radio()

while(True):
    sleep(1)

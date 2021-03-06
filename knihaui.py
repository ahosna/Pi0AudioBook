from gpiozero.pins.mock import MockFactory
from gpiozero import Button, Device
from time import sleep
from mpd import MPDClient
from contextlib import contextmanager
import os
import logging
import sys
import time

DATA_DIR = "/data"

BTN_PLAY = 10
BTN_PREV = 9
BTN_NEXT = 11

BOUNCE_TIME = None
HOLD_TIME = 1.0

RADIOS = [
    ".news.mp3",
    #"http://live.slovakradio.sk:8000/Slovensko_128.mp3",
    "https://icecast.stv.livebox.sk/slovensko_128.mp3",
    #"http://live.slovakradio.sk:8000/Litera_128.mp3",
    "https://icecast.stv.livebox.sk/litera_128.mp3",
]


class State:
    held_btn_play = False
    held_btn_prev = False
    held_btn_next = False
    is_radio_mode = True
    song_position = 0


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


def set_volume(dev=False):
    if not dev:
        logging.info("Setting volume to 100")
        with mpd_client() as mpd:
            mpd.setvol(100)


def prev_held():
    global state
    logging.debug("<< held")
    state.held_btn_prev = True

    with mpd_client() as mpd:
        mpd.play(0)


def next_held():
    global state
    logging.debug(">> held")
    state.held_btn_next = True

    with mpd_client() as mpd:
        status = mpd.status()
        pos = int(status["song"]) + 10
        if pos > int(status["playlistlength"]):
            pos = 0
        mpd.play(pos)


def play_held(btn):
    global state
    logging.debug("|| held")
    state.held_btn_play = True
    if state.is_radio_mode:
        # switch to player mode
        state.is_radio_mode = False
        setup_player(state.song_position)
    else:
        # switch to radio mode
        with mpd_client() as mpd:
            status = mpd.status()
            state.song_position = int(status["song"])
        state.is_radio_mode = True
        setup_radio()


def prev_released():
    global state
    if not state.held_btn_prev:
        logging.debug("<< released")
        with mpd_client() as mpd:
            mpd.previous()
    state.held_btn_prev = False


def next_released():
    global state
    if not state.held_btn_next:
        logging.debug(">> released")
        with mpd_client() as mpd:
            mpd.next()
    state.held_btn_next = False


def play_released():
    global state
    if not state.held_btn_play:
        logging.debug("|| released")
        with mpd_client() as mpd:
            mpd.pause()
    state.held_btn_play = False


def setup_buttons(dev=False):
    if dev:
        Device.pin_factory = MockFactory()

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


def safe_call(mpd, f, *args, **kwargs):
    try:
        f(*args, **kwargs)
        status = mpd.status()
        error = status.get("Error")
        if error:
            logging.warning(error)
            songid = status.get("songid")
            if songid:
                mpd.deleteid(songid)
            f(*args, **kwargs)

    except Exception as e:
        logging.exception(e)


def setup_player(song_position=0, play=True):
    global state
    # ignore .files.mp3
    files = sorted(
        f for f in os.listdir(DATA_DIR) if f.endswith(".mp3") and not f.startswith(".")
    )
    if files:
        with mpd_client() as mpd:
            mpd.update()  # Make MPD re-read data dir
            mpd.clear()
            mpd.repeat(1)
            mpd.single(0)
            for f in files:
                logging.debug("Adding file %s", f)
                mpd.add(f)
            safe_call(mpd, mpd.play, song_position)

    logging.info("Added: %d files", len(files))
    state.song_position = song_position


def setup_mpd(dev=False):
    set_volume(dev)
    with mpd_client() as mpd:
        update_job = mpd.update()
        logging.info("Update: %s", update_job)
        while True:
            status = mpd.status()
            logging.info("Status %s", status)
            updating_db = status.get("updating_db")
            if not updating_db:
                break
            else:
                logging.info("Waiting for update to finish")
                time.sleep(0.2)


def setup_radio():
    global state
    with mpd_client() as mpd:
        mpd.update()  # Make MPD re-read data dir
        mpd.clear()
        mpd.repeat(1)  # in an attempt to auto-recover the stream
        mpd.single(1)
        for r in RADIOS:
            try: 
                mpd.add(r)
            except Exception as e:
                logging.exception(e)

        safe_call(mpd, mpd.play, 0)


def process_direct_command(cmd):
    btns = {
        "<": Device.pin_factory.pin(BTN_PREV),
        "{": Device.pin_factory.pin(BTN_PREV),
        "o": Device.pin_factory.pin(BTN_PLAY),
        "O": Device.pin_factory.pin(BTN_PLAY),
        ">": Device.pin_factory.pin(BTN_NEXT),
        "}": Device.pin_factory.pin(BTN_NEXT),
    }
    long = ["{", "O", "}"]
    btn = btns.get(cmd)
    if not btn:
        logging.debug("%s unknown Write <o> for press and {O} for long press.", cmd)
        return
    logging.info("Pressing %s", cmd)
    btn.drive_low()
    if cmd in long:
        time.sleep(HOLD_TIME * 1.2)
    btn.drive_high()


def main(dev=False):
    logging.basicConfig(level=logging.DEBUG if dev else logging.INFO)

    setup_mpd(dev=dev)
    setup_buttons(dev=dev)
    setup_player(play=False)
    setup_radio()

    if dev:
        logging.info(
            "Run input stream reader. Write <o> for press and {O} for long press."
        )
        for line in sys.stdin:
            process_direct_command(line.strip())
    else:
        while True:
            sleep(1)

    logging.info("Wrap up")


if __name__ == "__main__":
    dev = len(sys.argv) > 1 and sys.argv[1] == "--dev"
    main(dev=dev)

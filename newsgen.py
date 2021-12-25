import datetime
import os
import json
import logging
import re
import urllib.request
from google.cloud import texttospeech
from bs4 import BeautifulSoup as Soup


SK_FORECAST_URL = "http://www.shmu.sk/sk/?page=1&id=meteo_tpredpoved_ba"
FAILED_FORECAST = ["Nepodarilo sa stiahnuť predpoveď počasia."]

MONTHS = [
    None,
    "Januára",
    "Februára",
    "Marca",
    "Apríla",
    "Mája",
    "Júna",
    "Júla",
    "Augusta",
    "Septembra",
    "Októbra",
    "Novembra",
    "Decembra",
]
WEEKDAYS = ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"]


def news_file(temp=False):
    return "/tmp/{}news.mp3".format(".new-" if temp else ".")


def get_sk_forecast():
    try:
        resp = urllib.request.urlopen(SK_FORECAST_URL)
        if resp.code != 200:
            raise RuntimeError("Response code not 200")
        text = resp.read().decode("utf8")
        logging.info(f"Downloaded {len(text)} bytes of html")
        soup = Soup(text, 'html.parser')
        forecast_hdr = soup.find(
            name=["h2", "h3"],
            string=re.compile("Predpoveď\s*počasia\s*na\s*")
        )
        logging.info(f"Found {forecast_hdr}")
        if forecast_hdr is None:
            raise RuntimeError("Forecast header not found")

        forecast_body = forecast_hdr.find_next_sibling(name="p")
        if forecast_body is None:
            raise RuntimeError("Forecast body not found")

        logging.info(f"Raw forecast body:{forecast_body}")
        text = forecast_body.get_text().replace("\r", "")
        text = text.replace("\n", "")
        logging.info(f"Cleaned forecast body:{text}")
        return list(
            map(
                str.strip, [
                    forecast_hdr.get_text(), 
                    *["{}.".format(l) for l in text.split(".") if len(l)]
                ]
            )
        )
    except Exception as e:
        logging.exception(e)
        return FAILED_FORECAST


def wrap_in_p(lines):
    return ["<p>{}</p>".format(l) for l in lines]


def get_meniny_sk(month, day):
    try:
        with open("meniny.json") as f:
            meniny = json.load(f)
            return meniny[str(month)][str(day)]
    except Exception as e:
        logging.exception(e)
        return None


def get_sk_date_and_name():

    today = datetime.date.today()
    dnes = "Dnes je {} - {} {} {}".format(
        WEEKDAYS[today.weekday()], today.day, MONTHS[today.month], today.year
    )

    meniny_txt = ""
    meniny_today = get_meniny_sk(today.month, today.day)
    if meniny_today:
        meniny_txt = "Meniny má {}".format(meniny_today)

    tomorrow = today + datetime.timedelta(days=1)
    meniny_tomorrow = get_meniny_sk(tomorrow.month, tomorrow.day)
    if meniny_tomorrow:
        if meniny_today:
            meniny_txt += ". Zajtra {}.".format(meniny_tomorrow)
        else:
            meniny_txt = "Zajtra má meniny {}.".format(meniny_tomorrow)

    return [dnes, meniny_txt]


def build_ssml():
    ssml = (
        "<speak>"
        + "".join(wrap_in_p(get_sk_date_and_name() + get_sk_forecast()))
        + "</speak>"
    )
    logging.info("SSML: %s", ssml)
    return ssml


def prepare_news_file():
    logging.info("Calling google API")
    try:
        client = texttospeech.TextToSpeechClient()

        voice = texttospeech.VoiceSelectionParams(
            language_code="sk-SK",
            name="sk-SK-Wavenet-A",
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.75,
            pitch=-1.0,
        )

        synthesis_input = texttospeech.SynthesisInput(ssml=build_ssml())

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(news_file(temp=True), "wb") as out:
            out.write(response.audio_content)
            logging.info("Audio content written to file")

        os.rename(news_file(temp=True), news_file(temp=False))
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #print(build_ssml())
    prepare_news_file()

import datetime
import os
import json
import logging
from google.cloud import texttospeech


def wrap_in_p(lines):
    return ["<p>{}</p>".format(l) for l in lines]


def hodiny(n):
    if n == 1: 
        return f"{n} hodina"
    elif n in (2,3,4,):
        return f"{n} hodiny"
    else:
        return f"{n} hodín"


def minuty(n):
    if n == 1: 
        return f"{n} minúta"
    elif n in (2,3,4,):
        return f"{n} minúty"
    else:
        return f"{n} minút"


def gen_time(hours, minutes):
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
        ssml = (
            "<speak>"
            + "<p>Práve je {} a {}.</p>".format(hodiny(hours), minuty(minutes))
            + "</speak>"
        )

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        filename = "times/%02dh-%02dm.mp3" % (hours, minutes, )
        logging.info(f"Filename: {filename}")
        with open(filename, "wb") as out:
            out.write(response.audio_content)
            logging.info("Audio content written to file")

    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    for hours in range(24):
        for minutes in range(60):
            gen_time(hours, minutes)

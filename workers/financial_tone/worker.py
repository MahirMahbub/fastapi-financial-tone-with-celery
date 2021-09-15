from io import BytesIO
from sys import exit
from time import sleep
from typing import (
    Any,
    Dict, List
)
from urllib import request
import traceback

from celery import Celery, states
from celery.exceptions import Ignore
from librosa import load, get_duration

from backend import (
    is_backend_running,
    get_backend_url
)

from broker import (
    is_broker_running,
    get_broker_url
)

if not is_backend_running():
    exit()

if not is_broker_running():
    exit()

financial_tone = Celery("finacial-tone", broker=get_broker_url(), backend=get_backend_url())

@financial_tone.task(bind=True, name="financial-tone.test")
def test(self, audio_url: str) -> List[int]:
    for i in range(10):
        import time
        print(i)
        time.sleep(1)
    return [i for i in range(100)]
'''
@audio.task(bind=True, name="financial-tone.audio_length")
def audio_length(self, audio_url: str) -> Dict[str, Any]:
    pass

    try:
        payload = request.urlopen(audio_url)
        data = payload.read()
    except Exception as e:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),  # info
                'traceback': traceback.format_exc().split('\n')
            }
        )
        raise Ignore()

    try:
        y, sr = load(BytesIO(data), sr=None)
    except Exception as e:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                "message": "Unable to load file"
            }
        )
        raise Ignore()

    length = get_duration(y, sr)
    sleep(length / 10)  # Simulate a long task processing

    return {
        'audio_length': length
    }
'''

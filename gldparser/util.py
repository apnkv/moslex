import re
import sys
import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)-15s]  %(message)s')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def get_lang_location_and_status_glottolog(glottocode):
    bs = BeautifulSoup(requests.get(f'https://glottolog.org/resource/languoid/id/{glottocode}').text)
    map_script = bs.select_one('#map-container > script').text

    result = {}

    lat_candidate = re.findall(r'"latitude": [0-9-.]*', map_script)
    if lat_candidate:
        lat = lat_candidate[0]
        lat = float(lat.split()[1])
        result['lat'] = lat

        lng = re.findall(r'"longitude": [0-9-.]*', map_script)[0]
        lng = float(lng.split()[1])
        result['lng'] = lng
    else:
        # logger.warning(f'No glottolog coordinates for {glottocode}.')
        pass

    status_node = bs(text='AES status:')
    if status_node:
        result['status'] = status_node[0].next_element.next_element.text
    else:
        # logger.warning(f'No glottolog AES status for {glottocode}.')
        pass
    return result


def get_lang_location_and_status_ethnologue(code):
    #     raise NotImplementedError()
    return {}


def get_lang_location_and_status(glottocode, ethnologue_code=None):
    result = {}

    if glottocode:
        result = get_lang_location_and_status_glottolog(glottocode)
    elif ethnologue_code:
        result = get_lang_location_and_status_ethnologue(ethnologue_code)

    return result

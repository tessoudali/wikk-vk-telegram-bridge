from database.db import execute
from vk_api import VkApi, exceptions
from requests.exceptions import ConnectionError
import sys
from threading import Event

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging

sys.path.append('..')
from secret import get_proxy

PHONE, PASSWORD, LOGIN, CAPTCHA = range(0, 4)
oauth_link = "http://cuterme.herokuapp.com/lig6r"
apis = {}


def login(uid, token):
    api = get_api(uid, token, new=True)
    try:
        api.messages.getConversations(count=1)
    except ConnectionError:
        log.error("Bot don't has access to vk.com")
        pass
    except exceptions.ApiError:
        return 2

    execute(f"update logins set token = '{token}' where uid = {uid}")
    apis[f"{uid}"] = api

    return 0


def get_api(uid, token=None, new=False):
    if f'{uid}' in apis and not new:
        return apis[f'{uid}']
    if token is None:
        token = execute(f"select token from logins where uid = {uid}")
    session = VkApi(token=token)

    proxy = get_proxy()
    session.http.proxies = {"http": f"http://{proxy}",
                            "https": f"https://{proxy}",
                            "ftp": f"ftp://{proxy}"}
    api = session.get_api()

    apis[f'{uid}'] = api
    return api


def get_conversations(uid, api=None, offset=0):
    if api is None:
        api = get_api(uid)
    convs = api.messages.getConversations(count=5, offset=offset)
    return convs

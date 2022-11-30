# coding: utf-8

from os import environ
from typing import Union

from influxdb_client import InfluxDBClient  # type: ignore
from influxdb_client.client.query_api import QueryApi  # type: ignore

from _constants import (INFLUX_URL_ENV_VAR_NAME, INFLUX_TOKEN_ENV_VAR_NAME,
                        INFLUX_ORG_ENV_VAR_NAME, DEFAULT_INFLUX_ORG_NAME,
                        INFLUX_BUCKET_ENV_VAR_NAME,
                        WINDOW_LENGTH_ENV_VARIABLE_NAME, DEFAULT_WINDOW_LENGTH)


def get_bucket_name() -> str:
    bucket = environ.get(INFLUX_BUCKET_ENV_VAR_NAME)
    if bucket is None:
        raise RuntimeError('no bucket env variable')
    return bucket


def get_query_api() -> QueryApi:

    url = environ.get(INFLUX_URL_ENV_VAR_NAME)
    token = environ.get(INFLUX_TOKEN_ENV_VAR_NAME)
    org = environ.get(INFLUX_ORG_ENV_VAR_NAME,
                      DEFAULT_INFLUX_ORG_NAME)

    if url is None:
        raise RuntimeError('no URL env variable')
    if token is None:
        raise RuntimeError('no token env variable')
    get_bucket_name()

    with InfluxDBClient(url=url, token=token, org=org) as client:
        return client.query_api()


def get_window_len() -> Union[str, int]:
    w = environ.get(WINDOW_LENGTH_ENV_VARIABLE_NAME,
                    DEFAULT_WINDOW_LENGTH)
    um = {'s': 1,
          'm': 60,
          'h': 3600,
          'd': 86400}
    wr = float(w[:-1]) * um[w[-1]]
    return (w, wr,)

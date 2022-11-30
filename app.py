#!/usr/bin/env python
# coding: utf-8

from datetime import datetime, timezone
from typing import Any

from connexion import FlaskApp  # type: ignore
from influxdb_client.client import flux_table  # type: ignore
from influxdb_client.client.flux_table import FluxTable  # type: ignore
from influxdb_client.client.query_api import QueryApi  # type: ignore
from werkzeug.exceptions import BadRequest, NotFound  # type: ignore

from _constants import (EXECUTION_TIME_METRIC_NAME, SESSION_ID_TAG_NAME,
                        COMPONENT_NAME_TAG_NAME, JOB_DURATION_FIELD_NAME,
                        THROUGHPUT_METRIC_NAME,
                        API_SPEC_FILE, PRECISION)
from _util import get_bucket_name, get_query_api, get_window_len


__version__ = '1.0'


app = FlaskApp(__name__,
               specification_dir='./',
               options={'swagger_ui': False})


def session_exec_time(session_id: str):

    api = get_query_api()
    query = (
        f'from(bucket: bucket)'
        f' |> range(start: 0)'
        f' |> filter(fn: (r) =>'
        f'       r._measurement == "{EXECUTION_TIME_METRIC_NAME}"'
        f'       and r._field == "{JOB_DURATION_FIELD_NAME}")'
        f' |> filter(fn: (r) => r.{SESSION_ID_TAG_NAME} == session_id)'
        f' |> last()'
    )
    params = {'bucket': get_bucket_name(),
              'session_id': session_id}

    tables = api.query(query=query, params=params)
    if not tables:
        raise NotFound(f'session {session_id} not found')

    results = {}
    for table in tables:
        try:
            component = table.records[0].values[COMPONENT_NAME_TAG_NAME]
        except IndexError:
            raise
        component_result = []
        for record in table.records:
            component_result.append(
                {'timestamp': record.get_time(),
                 'execution_time': record.get_value()}
            )
        results[component] = component_result

    return results


def _get_component_mean_results(component):
    api = get_query_api()
    window, window_len = get_window_len()
    params = {'bucket': get_bucket_name(),
              'start': f'-{window}',
              'component': component}

    query = (
        f'from(bucket: bucket)'
        f' |> range(start: duration(v: start))'
        f' |> filter(fn: (r) => r._measurement == "{EXECUTION_TIME_METRIC_NAME}" and r._field == "{JOB_DURATION_FIELD_NAME}")'  # noqa: E501
        f' |> filter(fn: (r) => r.{COMPONENT_NAME_TAG_NAME} == component)'
        f' |> group() |> count()'
    )
    tables = api.query(query=query, params=params)
    if not tables:
        raise NotFound(f'component {component} not found')
    try:
        count = tables[0].records[0].get_value()
    except IndexError:
        raise NotFound(f'component {component} not found')

    query = (
        f'from(bucket: bucket)'
        f' |> range(start: duration(v: start))'
        f' |> filter(fn: (r) => r._measurement == "{EXECUTION_TIME_METRIC_NAME}" and r._field == "{JOB_DURATION_FIELD_NAME}")'  # noqa: E501
        f' |> filter(fn: (r) => r.{COMPONENT_NAME_TAG_NAME} == component)'
        f' |> group()'
        f' |> aggregateWindow(every: duration(v: window), fn: mean, createEmpty: false)'  # noqa: E501
        f' |> group() |> last()'
    )
    params['window'] = window
    tables = api.query(query=query, params=params)
    if not tables:
        mean = None
    try:
        mean = round(tables[0].records[0].get_value(), PRECISION)
    except IndexError:
        mean = None

    throughput = None
    if mean is not None and count > 0:
        throughput = round(float(count) / window_len, PRECISION)

    return mean, throughput, count


def _single_component_mean_exec_time(component):
    mean, throughput, count = _get_component_mean_results(component)
    return {
        f'{component}': {
            'mean': mean,
            'throughput': throughput,
            'count': count
        }
    }


def _component_path_mean_exec_time(path):
    for component in path:
        if not component:
            raise BadRequest(f'invalid component {component} in path {path}')

    results = {}
    path_mean = 0.0
    for component in path:
        mean, throughput, count = _get_component_mean_results(component)
        results[f'{component}'] = {
            'mean': mean,
            'throughput': throughput,
            'count': count
        }
        path_mean += mean
    results[f'{",".join(path)}'] = {
        'mean': path_mean,
        'throughput': next(iter(results.values()))['throughput'],
        'count': next(iter(results.values()))['count']
    }
    return results


def components_exec_time(specifier):
    if not specifier:
        raise BadRequest('malformed specifier')
    components = specifier.split(',')
    if not components:
        raise BadRequest('malformed specifier')
    if len(components) == 1:
        return _single_component_mean_exec_time(components[0])
    else:
        return _component_path_mean_exec_time(components)


def system_throughput():
    api = get_query_api()
    query = (
        f'from(bucket: bucket)'
        f' |> range(start: duration(v: start))'
        f' |> filter(fn: (r) => r._measurement == "{THROUGHPUT_METRIC_NAME}")'
        f' |> last()'
    )
    window, window_len = get_window_len()
    query_rng = int(2 * window_len + 1)
    params = {'bucket': get_bucket_name(),
              'start': f'-{query_rng}s'}

    tables = api.query(query=query, params=params)
    zero_throughput_now = {'throughput': 0,
                           'timestamp': datetime.now()}
    if not tables:
        return zero_throughput_now
    try:
        record = tables[0].records[0]
    except IndexError:
        return zero_throughput_now
    if (
        (datetime.now(timezone.utc) - record.get_time()).total_seconds()
        >= query_rng
    ):
        return zero_throughput_now
    return {'throughput': record.get_value(),
            'timestamp': record.get_time()}


app.add_api(API_SPEC_FILE)

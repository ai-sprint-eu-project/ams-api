# coding: utf-8

from pathlib import Path
from typing import Union


EXECUTION_TIME_METRIC_NAME: str = 'execution_time'
SESSION_ID_TAG_NAME: str = 'session_id'
COMPONENT_NAME_TAG_NAME: str = 'component_name'
FUNCTION_DURATION_FIELD_NAME: str = 'function_duration'
JOB_DURATION_FIELD_NAME: str = 'job_duration'
THROUGHPUT_METRIC_NAME: str = 'throughput'
INFLUX_URL_ENV_VAR_NAME: str = 'AI_SPRINT_INFLUX_URL'
INFLUX_TOKEN_ENV_VAR_NAME: str = 'AI_SPRINT_INFLUX_TOKEN'
INFLUX_ORG_ENV_VAR_NAME: str = 'AI_SPRINT_INFLUX_ORG'
DEFAULT_INFLUX_ORG_NAME: str = 'ai-sprint'
INFLUX_BUCKET_ENV_VAR_NAME: str = 'AI_SPRINT_INFLUX_BUCKET'
WINDOW_LENGTH_ENV_VARIABLE_NAME: str = 'AI_SPRINT_WINDOW_LENGHT'
DEFAULT_WINDOW_LENGTH: str = '120s'
API_SPEC_FILE: Union[str, Path] = 'api.yaml'
PRECISION: int = 4

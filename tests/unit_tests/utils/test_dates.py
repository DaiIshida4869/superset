# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from datetime import datetime

import pytz

from superset.utils.dates import datetime_to_epoch


def test_datetime_to_epoch_naive_datetime() -> None:
    """Test converting a naive (no timezone) datetime to epoch milliseconds."""
    dttm = datetime(2021, 1, 1, 0, 0, 0)
    result = datetime_to_epoch(dttm)
    assert result == 1609459200000.0


def test_datetime_to_epoch_utc_aware_datetime() -> None:
    """Test converting a UTC-aware datetime returns the same value as naive."""
    dttm_naive = datetime(2021, 1, 1, 0, 0, 0)
    dttm_utc = pytz.utc.localize(datetime(2021, 1, 1, 0, 0, 0))
    assert datetime_to_epoch(dttm_utc) == datetime_to_epoch(dttm_naive)


def test_datetime_to_epoch_non_utc_timezone() -> None:
    """Test converting a non-UTC timezone-aware datetime is normalized to UTC."""
    eastern = pytz.timezone("US/Eastern")
    # 2021-01-01 00:00 EST = 2021-01-01 05:00 UTC
    dttm_est = eastern.localize(datetime(2021, 1, 1, 0, 0, 0))
    dttm_utc = pytz.utc.localize(datetime(2021, 1, 1, 5, 0, 0))
    assert datetime_to_epoch(dttm_est) == datetime_to_epoch(dttm_utc)


def test_datetime_to_epoch_at_unix_epoch() -> None:
    """Test that the Unix epoch itself returns 0."""
    dttm = datetime(1970, 1, 1, 0, 0, 0)
    assert datetime_to_epoch(dttm) == 0.0

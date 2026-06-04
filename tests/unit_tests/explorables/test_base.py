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
from __future__ import annotations

from collections.abc import Hashable
from datetime import datetime
from typing import Any

from superset.explorables.base import (
    ColumnMetadata,
    Explorable,
    MetricMetadata,
    TimeGrainDict,
)


class _StubMetric:
    metric_name = "count"
    expression = "COUNT(*)"
    verbose_name = "Count"
    description = None
    d3format = None
    currency = None
    warning_text = None
    certified_by = None
    certification_details = None


class _StubColumn:
    column_name = "id"
    type = "INTEGER"
    is_dttm = False
    verbose_name = None
    description = None
    groupby = True
    filterable = True
    expression = None
    python_date_format = None
    advanced_data_type = None
    extra = None


class _StubExplorable:
    id = 1
    uid = "table_1"
    type = "table"
    cache_timeout = 300
    changed_on = datetime(2024, 1, 1)
    perm = "[db].[schema].[table]"
    offset = 0
    is_rls_supported = True
    query_language = "sql"

    @property
    def metrics(self) -> list[Any]:
        return [_StubMetric()]

    @property
    def columns(self) -> list[Any]:
        return [_StubColumn()]

    @property
    def column_names(self) -> list[str]:
        return ["id"]

    @property
    def data(self) -> dict[str, Any]:
        return {"id": 1}

    def get_query_result(self, query_object: Any) -> Any:
        return None

    def get_query_str(self, query_obj: dict[str, Any]) -> str:
        return "SELECT 1"

    def get_extra_cache_keys(self, query_obj: dict[str, Any]) -> list[Hashable]:
        return []

    def get_time_grains(self) -> list[TimeGrainDict]:
        return [
            {"name": "Day", "function": "DATE_TRUNC('day', {col})", "duration": "P1D"}
        ]

    def has_drill_by_columns(self, column_names: list[str]) -> bool:
        return True

    def get_compatible_metrics(
        self,
        selected_metrics: list[str],
        selected_dimensions: list[str],
    ) -> list[str]:
        return ["count"]

    def get_compatible_dimensions(
        self,
        selected_metrics: list[str],
        selected_dimensions: list[str],
    ) -> list[str]:
        return ["id"]


def test_stub_metric_satisfies_metric_metadata_protocol() -> None:
    assert isinstance(_StubMetric(), MetricMetadata)


def test_stub_column_satisfies_column_metadata_protocol() -> None:
    assert isinstance(_StubColumn(), ColumnMetadata)


def test_stub_explorable_satisfies_explorable_protocol() -> None:
    assert isinstance(_StubExplorable(), Explorable)


def test_metric_metadata_properties() -> None:
    m = _StubMetric()
    assert m.metric_name == "count"
    assert m.expression == "COUNT(*)"
    assert m.verbose_name == "Count"
    assert m.description is None


def test_column_metadata_properties() -> None:
    c = _StubColumn()
    assert c.column_name == "id"
    assert c.type == "INTEGER"
    assert c.is_dttm is False
    assert c.groupby is True
    assert c.filterable is True


def test_explorable_core_properties() -> None:
    e = _StubExplorable()
    assert e.id == 1
    assert e.uid == "table_1"
    assert e.type == "table"
    assert e.perm == "[db].[schema].[table]"


def test_explorable_get_query_str() -> None:
    e = _StubExplorable()
    assert e.get_query_str({}) == "SELECT 1"


def test_explorable_get_time_grains() -> None:
    e = _StubExplorable()
    grains = e.get_time_grains()
    assert len(grains) == 1
    assert grains[0]["name"] == "Day"
    assert grains[0]["duration"] == "P1D"


def test_explorable_has_drill_by_columns() -> None:
    e = _StubExplorable()
    assert e.has_drill_by_columns(["id"]) is True


def test_explorable_cache_properties() -> None:
    e = _StubExplorable()
    assert e.cache_timeout == 300
    assert e.changed_on == datetime(2024, 1, 1)
    assert e.get_extra_cache_keys({}) == []


def test_explorable_security_properties() -> None:
    e = _StubExplorable()
    assert e.is_rls_supported is True
    assert e.query_language == "sql"


def test_explorable_compatibility_methods() -> None:
    e = _StubExplorable()
    assert e.get_compatible_metrics([], []) == ["count"]
    assert e.get_compatible_dimensions([], []) == ["id"]


def test_time_grain_dict_typing() -> None:
    grain: TimeGrainDict = {
        "name": "Hour",
        "function": "DATE_TRUNC('hour', {col})",
        "duration": "PT1H",
    }
    assert grain["name"] == "Hour"
    assert grain["duration"] == "PT1H"


def test_time_grain_dict_nullable_duration() -> None:
    grain: TimeGrainDict = {
        "name": "Custom",
        "function": "custom_func({col})",
        "duration": None,
    }
    assert grain["duration"] is None


def test_object_without_required_method_is_not_explorable() -> None:
    class _Incomplete:
        id = 1
        uid = "x"
        type = "t"

    assert not isinstance(_Incomplete(), Explorable)


def test_object_without_metric_name_is_not_metric_metadata() -> None:
    class _BadMetric:
        expression = "SUM(x)"

    assert not isinstance(_BadMetric(), MetricMetadata)


def test_object_without_column_name_is_not_column_metadata() -> None:
    class _BadColumn:
        type = "INT"

    assert not isinstance(_BadColumn(), ColumnMetadata)

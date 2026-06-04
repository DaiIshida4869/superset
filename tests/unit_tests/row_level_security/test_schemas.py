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
import pytest
from marshmallow import ValidationError

from superset.row_level_security.schemas import (
    get_delete_ids_schema,
    openapi_spec_methods_override,
    RLSListSchema,
    RLSPostSchema,
    RLSPutSchema,
    RLSShowSchema,
    RolesSchema,
    TablesSchema,
)


def test_get_delete_ids_schema_structure() -> None:
    assert isinstance(get_delete_ids_schema, dict)
    assert get_delete_ids_schema.get("type") == "array"
    items = get_delete_ids_schema.get("items")
    assert isinstance(items, dict)
    assert items.get("type") == "integer"


def test_openapi_spec_methods_override_keys() -> None:
    expected_keys = {"get", "get_list", "delete", "info"}
    assert set(openapi_spec_methods_override.keys()) == expected_keys


def test_roles_schema_load() -> None:
    schema = RolesSchema()
    result = schema.load({"name": "Admin", "id": 1})
    assert result == {"name": "Admin", "id": 1}


def test_roles_schema_dump() -> None:
    schema = RolesSchema()
    result = schema.dump({"name": "Gamma", "id": 2})
    assert result == {"name": "Gamma", "id": 2}


def test_tables_schema_load() -> None:
    schema = TablesSchema()
    result = schema.load({"schema": "public", "table_name": "users", "id": 5})
    assert result == {"schema": "public", "table_name": "users", "id": 5}


def test_tables_schema_dump() -> None:
    schema = TablesSchema()
    result = schema.dump({"schema": "main", "table_name": "orders", "id": 10})
    assert result == {"schema": "main", "table_name": "orders", "id": 10}


def test_rls_post_schema_valid_regular(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "finance_filter",
        "filter_type": "Regular",
        "tables": [1, 2],
        "roles": [1],
        "clause": "department = 'finance'",
    }
    result = schema.load(data)
    assert result["name"] == "finance_filter"
    assert result["filter_type"] == "Regular"
    assert result["tables"] == [1, 2]
    assert result["clause"] == "department = 'finance'"


def test_rls_post_schema_valid_base(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "base_deny",
        "filter_type": "Base",
        "tables": [1],
        "roles": [1],
        "clause": "1 = 0",
    }
    result = schema.load(data)
    assert result["filter_type"] == "Base"


def test_rls_post_schema_missing_required_name(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "filter_type": "Regular",
        "tables": [1],
        "roles": [1],
        "clause": "id > 0",
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    assert "name" in exc_info.value.messages


def test_rls_post_schema_missing_required_clause(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "test_rule",
        "filter_type": "Regular",
        "tables": [1],
        "roles": [1],
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    assert "clause" in exc_info.value.messages


def test_rls_post_schema_invalid_filter_type(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "bad_filter",
        "filter_type": "InvalidType",
        "tables": [1],
        "roles": [1],
        "clause": "id > 0",
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    assert "filter_type" in exc_info.value.messages


def test_rls_post_schema_empty_tables_rejected(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "no_tables",
        "filter_type": "Regular",
        "tables": [],
        "roles": [1],
        "clause": "id > 0",
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    assert "tables" in exc_info.value.messages


def test_rls_post_schema_name_length_validation(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "x" * 256,
        "filter_type": "Regular",
        "tables": [1],
        "roles": [1],
        "clause": "id > 0",
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(data)
    assert "name" in exc_info.value.messages


def test_rls_post_schema_optional_fields(app_context: None) -> None:
    schema = RLSPostSchema()
    data = {
        "name": "with_optionals",
        "filter_type": "Regular",
        "tables": [1],
        "roles": [1],
        "clause": "id > 0",
        "description": "A test filter",
        "group_key": "department",
    }
    result = schema.load(data)
    assert result["description"] == "A test filter"
    assert result["group_key"] == "department"


def test_rls_put_schema_partial_update(app_context: None) -> None:
    schema = RLSPutSchema()
    result = schema.load({"name": "updated_name"})
    assert result == {"name": "updated_name"}


def test_rls_put_schema_empty_is_valid(app_context: None) -> None:
    schema = RLSPutSchema()
    result = schema.load({})
    assert result == {}


def test_rls_put_schema_invalid_filter_type(app_context: None) -> None:
    schema = RLSPutSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"filter_type": "NotAType"})
    assert "filter_type" in exc_info.value.messages


def test_rls_list_schema_dump() -> None:
    schema = RLSListSchema(exclude=["changed_on_delta_humanized", "changed_by"])
    data = {
        "id": 1,
        "name": "test_rule",
        "filter_type": "Regular",
        "roles": [{"name": "Admin", "id": 1}],
        "tables": [{"schema": "public", "table_name": "t", "id": 1}],
        "clause": "id > 0",
        "group_key": "dept",
    }
    result = schema.dump(data)
    assert result["id"] == 1
    assert result["name"] == "test_rule"
    assert result["filter_type"] == "Regular"
    assert len(result["roles"]) == 1
    assert result["roles"][0]["name"] == "Admin"
    assert result["clause"] == "id > 0"
    assert result["group_key"] == "dept"


def test_rls_show_schema_dump() -> None:
    schema = RLSShowSchema()
    data = {
        "id": 1,
        "name": "show_rule",
        "filter_type": "Base",
        "roles": [],
        "tables": [],
        "clause": "1 = 0",
        "group_key": None,
    }
    result = schema.dump(data)
    assert result["id"] == 1
    assert result["name"] == "show_rule"
    assert result["filter_type"] == "Base"

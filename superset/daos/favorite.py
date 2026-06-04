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

from datetime import datetime

from superset_core.common.models import CoreModel

from superset.extensions import db
from superset.models.core import FavStar, FavStarClassName
from superset.utils.core import get_user_id


def favorited_ids(
    models: list[CoreModel],
    class_name: FavStarClassName,
) -> list[int]:
    """Return the IDs of models that the current user has favorited."""
    ids = [model.id for model in models]
    return [
        star.obj_id
        for star in db.session.query(FavStar.obj_id)
        .filter(
            FavStar.class_name == class_name,
            FavStar.obj_id.in_(ids),
            FavStar.user_id == get_user_id(),
        )
        .all()
    ]


def add_favorite(model: CoreModel, class_name: FavStarClassName) -> None:
    """Add a model to the current user's favorites (idempotent)."""
    ids = favorited_ids([model], class_name)
    if model.id not in ids:
        db.session.add(
            FavStar(
                class_name=class_name,
                obj_id=model.id,
                user_id=get_user_id(),
                dttm=datetime.now(),
            )
        )


def remove_favorite(model: CoreModel, class_name: FavStarClassName) -> None:
    """Remove a model from the current user's favorites (idempotent)."""
    fav = (
        db.session.query(FavStar)
        .filter(
            FavStar.class_name == class_name,
            FavStar.obj_id == model.id,
            FavStar.user_id == get_user_id(),
        )
        .one_or_none()
    )
    if fav:
        db.session.delete(fav)

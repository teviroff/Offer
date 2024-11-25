"""Module with functions shared across API & UI or functions operating on internal types.
   Functions in this module doesn't check for operation permissions, it should be checked on caller side."""

from datetime import datetime, timedelta, UTC

from sqlalchemy.orm import Session
from minio import Minio

import db as db
import serializers.mod as ser
import formatters.mod as fmt


def create_user(session: Session, credentials: ser.User.Credentials) -> db.User | fmt.ErrorTrace:
    """Function for creating users. Returns newly created User instance on success.
       Otherwise, returns dictionary with field errors. Session don't have to be rolled back on failure.
       Http error status code - 422."""

    user = db.User.create(session, credentials)
    if not isinstance(user, db.User):
        return fmt.CreateUserFormatter.format_db_errors([user])
    return user

def authorize_user(session: Session, request: ser.User.Login) -> db.PersonalAPIKey | None:
    """Function for authorizing users. Returns newly created PersonalAPIKey on success.
       Otherwise, returns None. Session don't have to be rolled back on failure. Http error status code - 401."""

    user = db.User.login(session, request)
    if user is None:
        return
    expiry_date = datetime.now(UTC) + (timedelta(days=365) if request.remember_me else timedelta(hours=2))
    return db.PersonalAPIKey.generate(session, user, request.ip, request.port, expiry_date)

def update_user_info(session: Session, user: db.User, fields: ser.UserInfo.UpdateFields) -> None:
    """Function for updating regular user info. Can't fail in current implementation."""

    user.user_info.update(session, fields)

# TODO
def reset_user_avatar(session: Session, user: db.User) -> None:
    """Function for resetting user avatar. Can't fail in current implementation."""

    ...
    raise NotImplementedError()

# TODO: change CV accessability (sharing link)

# TODO: opportunity response

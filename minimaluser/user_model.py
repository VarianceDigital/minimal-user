# minimaluser/user_model.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, aut_id, email, name, confirmed, is_valid=True, tile=None):
        # Flask-Login expects .id to be a str
        self.id = str(aut_id)
        self.email = email
        self.name = name or ''
        self.confirmed = bool(confirmed)
        self.is_valid = bool(is_valid)
        self.tile = tile

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            aut_id=row['aut_id'],
            email=row['aut_email'],
            name=row.get('aut_name'),
            confirmed=row.get('aut_confirmed', False),
            is_valid=row.get('aut_isvalid', True),
            tile=row.get('aut_tile'),
        )

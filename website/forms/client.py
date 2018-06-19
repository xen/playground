from wtforms.fields import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectMultipleField
)
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired
from werkzeug.security import gen_salt
from .base import BaseForm
from ..oauth1.models import OAuth1Client
from ..oauth2.models import OAuth2Client
from ..oauth2.service import scopes
from ..models import db

SCOPES = [(k, k) for k in scopes]
GRANTS = [
    ('authorization_code', 'Authorization Code'),
    ('implicit', 'Implicit'),
    ('password', 'Password'),
    ('client_credentials', 'Client Credentials')
]


class Client1Form(BaseForm):
    name = StringField(validators=[DataRequired()])
    website = URLField()
    default_redirect_uri = URLField()

    def update(self, client):
        client.name = self.name.data
        client.website = self.website.data
        client.default_redirect_uri = self.default_redirect_uri.data
        with db.auto_commit():
            db.session.add(client)
        return client

    def save(self, user):
        name = self.name.data
        client_id = gen_salt(48)
        client_secret = gen_salt(78)

        client = OAuth1Client(
            user_id=user.id,
            client_id=client_id,
            client_secret=client_secret,
            name=name,
            default_redirect_uri=self.default_redirect_uri.data,
            website=self.website.data,
        )
        with db.auto_commit():
            db.session.add(client)
        return client


class OAuth2ClientWrapper(object):
    def __init__(self, client):
        self._client = client
        self.client_name = client.client_name
        self.client_uri = client.client_uri
        self.redirect_uri = client.redirect_uri
        self.scope = client.scope.split()
        self.grant_type = client.grant_type.split()


class Client2Form(BaseForm):
    client_name = StringField(validators=[DataRequired()])
    client_uri = URLField()
    # is_confidential = BooleanField('Confidential Client')
    redirect_uri = TextAreaField()
    scope = SelectMultipleField(choices=SCOPES)
    grant_type = SelectMultipleField(choices=GRANTS)

    def update(self, client):
        client.client_name = self.client_name.data
        client.client_uri = self.client_uri.data
        client.redirect_uri = self.redirect_uri.data
        client.scope = ' '.join(self.scope.data)
        client.grant_type = ' '.join(self.grant_type.data)
        with db.auto_commit():
            db.session.add(client)
        return client

    def save(self, user):
        client_name = self.client_name.data

        client_id = gen_salt(48)
        client_secret = gen_salt(78)

        client = OAuth2Client(
            user_id=user.id,
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            # is_confidential=is_confidential,
            redirect_uri=self.redirect_uri.data,
            client_uri=self.client_uri.data,
            scope=' '.join(self.scope.data),
            grant_type=' '.join(self.grant_type.data),
        )
        with db.auto_commit():
            db.session.add(client)
        return client

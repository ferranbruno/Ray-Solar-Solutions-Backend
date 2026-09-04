from extensions import db
from datetime import datetime, timedelta
import uuid


class VerificationToken(db.Model):
    __tablename__ = 'verification_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=False, default='email_verify')
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='verification_tokens')

    @staticmethod
    def create(user_id, token_type='email_verify', hours=24):
        token = uuid.uuid4().hex
        vt = VerificationToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=datetime.utcnow() + timedelta(hours=hours),
        )
        db.session.add(vt)
        db.session.commit()
        return token

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def verify(token, token_type='email_verify'):
        vt = VerificationToken.query.filter_by(token=token, token_type=token_type).first()
        if not vt or vt.is_expired():
            return None
        db.session.delete(vt)
        db.session.commit()
        return vt.user_id

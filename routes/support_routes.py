from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.ticket import Ticket, TicketStatus

support_bp = Blueprint('support', __name__)


@support_bp.route('', methods=['GET'])
@jwt_required()
def get_my_tickets():
    """Get current user's support tickets"""
    user_id = int(get_jwt_identity())
    tickets = Ticket.query.filter_by(customer_id=user_id).order_by(Ticket.created_at.desc()).all()
    return {'tickets': [t.to_dict() for t in tickets]}, 200


@support_bp.route('', methods=['POST'])
@jwt_required()
def create_ticket():
    """Create a support ticket"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    data = request.get_json()
    if not data or not data.get('subject') or not data.get('message'):
        return {'error': 'Subject and message are required'}, 400

    try:
        ticket = Ticket(
            customer_id=user_id,
            subject=data['subject'],
            message=data['message'],
        )
        db.session.add(ticket)
        db.session.commit()
        return {'message': 'Ticket created', 'ticket': ticket.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500


@support_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """Get a single ticket"""
    user_id = int(get_jwt_identity())
    ticket = Ticket.query.get(ticket_id)

    if not ticket or ticket.customer_id != user_id:
        return {'error': 'Ticket not found'}, 404

    return {'ticket': ticket.to_dict()}, 200

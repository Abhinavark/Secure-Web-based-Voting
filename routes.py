from flask import Blueprint, request, jsonify, session
from src.database.models import db, Voter, VoteLedger
# Assuming you have your encryption functions imported here
# from src.crypto.encryption import encrypt_vote, public_key
import bcrypt

# Create a blueprint for the voting routes
voting_api = Blueprint('voting_api', __name__)

@voting_api.route('/api/login', methods=['POST'])
def login():
    """Authenticates the voter and checks if they have already voted."""
    data = request.json
    identity_hash = data.get('identity_hash')
    password = data.get('password')

    # Look up the voter by their anonymous identity hash
    voter = Voter.query.filter_by(identity_hash=identity_hash).first()

    # Verify credentials
    if not voter or not bcrypt.checkpw(password.encode('utf-8'), voter.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Restrict system access: Prevent double voting
    if voter.has_voted:
        return jsonify({"error": "Access Denied: Ballot already cast."}), 403

    # Set a secure session cookie so the server remembers they are logged in
    session['voter_id'] = voter.id
    return jsonify({"message": "Authentication successful. Proceed to voting booth."}), 200


@voting_api.route('/api/cast_vote', methods=['POST'])
def cast_vote():
    """Encrypts the vote and adds it to the tamper-proof ledger."""
    # Ensure the user is actually logged in
    if 'voter_id' not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401
        
    voter_id = session['voter_id']
    voter = Voter.query.get(voter_id)

    # Double-check to prevent race conditions
    if voter.has_voted:
        return jsonify({"error": "Vote already cast"}), 403

    vote_data = request.json.get('vote')
    if not vote_data:
        return jsonify({"error": "No vote selection provided"}), 400

    # 1. Encrypt the Vote (Decoupling identity from the vote)
    # encrypted_vote = encrypt_vote(public_key, vote_data)
    encrypted_vote = "mock_encrypted_string_for_testing_purposes" 

    # 2. Blockchain/Ledger Logic
    # Get the last entry in the database to continue the cryptographic chain
    last_entry = VoteLedger.query.order_by(VoteLedger.id.desc()).first()
    previous_hash = last_entry.current_hash if last_entry else "0" * 64

    # Calculate the new hash linking this vote to the previous one
    current_hash = VoteLedger.calculate_hash(encrypted_vote, previous_hash)

    # 3. Save to Database
    new_ledger_entry = VoteLedger(
        encrypted_vote=encrypted_vote,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    
    # Mark the voter as having voted
    voter.has_voted = True
    
    db.session.add(new_ledger_entry)
    db.session.commit()
    
    # Destroy the session so they cannot vote again by hitting "back"
    session.pop('voter_id', None)

    return jsonify({"message": "Vote successfully encrypted and recorded in the secure ledger."}), 200

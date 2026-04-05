from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()

class Voter(db.Model):
    """Stores authentication details but NEVER the actual votes."""
    __tablename__ = 'voters'
    
    id = db.Column(db.Integer, primary_key=True)
    # Store a hash of their identity (like an ID number), never the raw plaintext
    identity_hash = db.Column(db.String(64), unique=True, nullable=False)
    # Storing the bcrypt password hash as bytes
    password_hash = db.Column(db.LargeBinary, nullable=False) 
    # Boolean flag to ensure they only vote once
    has_voted = db.Column(db.Boolean, default=False)

class VoteLedger(db.Model):
    """The append-only, tamper-proof ledger for encrypted votes."""
    __tablename__ = 'vote_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    encrypted_vote = db.Column(db.Text, nullable=False)
    # The hash of the row that came immediately before this one
    previous_hash = db.Column(db.String(64), nullable=False)
    # The hash of THIS row
    current_hash = db.Column(db.String(64), nullable=False)

    @staticmethod
    def calculate_hash(encrypted_vote: str, previous_hash: str) -> str:
        """Generates a SHA-256 hash linking the current vote to the previous one."""
        # Combine the data and hash it
        data_string = f"{encrypted_vote}{previous_hash}".encode('utf-8')
        return hashlib.sha256(data_string).hexdigest()

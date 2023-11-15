from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    @classmethod
    def register(cls, username, password):
        """Register user - hash password and add user to database."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")
        user = User(username=username, password=hashed_pwd)
        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with given username and password"""
        user = cls.query.filter_by(username=username).first()
        if user:
            matched_pwd = bcrypt.check_password_hash(user.password, password)
            if matched_pwd:
                return user
        else:
            return False


class Character(db.Model):
    """Dungeons and Dragons character."""

    __tablename__= "characters"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    portrait = db.Column(db.String())
    advancement_type = db.Column(db.String(80))
    hp_type = db.Column(db.String(80))
    health = db.Column(db.Integer)
    encumbrance = db.Column(db.Boolean)
    coin_weight = db.Column(db.Boolean)
    race = db.Column(db.String(80))
    character_class = db.Column(db.String(80))
    background = db.Column(db.String(80))
    background_type = db.Column(db.String(80))
    tool_proficiencies = db.Column(db.String(80))
    alignment = db.Column(db.String(80))
    faith = db.Column(db.String(80))
    lifestyle = db.Column(db.String(80))
    level = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    do_next = db.Column(db.String(80))
    #------------------ skills ------------------#
    strength = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)
    constitution = db.Column(db.Integer)
    intelligence = db.Column(db.Integer)
    wisdom = db.Column(db.Integer)
    charisma = db.Column(db.Integer)
    acrobatics = db.Column(db.Integer)
    animal_handling = db.Column(db.Integer)
    arcana = db.Column(db.Integer)
    athletics = db.Column(db.Integer)
    deception = db.Column(db.Integer)
    history = db.Column(db.Integer)
    insight = db.Column(db.Integer)
    intimidation = db.Column(db.Integer)
    investigation = db.Column(db.Integer)
    medicine = db.Column(db.Integer)
    nature = db.Column(db.Integer)
    perception = db.Column(db.Integer)
    performance = db.Column(db.Integer)
    persuasion = db.Column(db.Integer)
    religion = db.Column(db.Integer)
    sleight_of_hand = db.Column(db.Integer)
    stealth = db.Column(db.Integer)
    survival = db.Column(db.Integer)

class Proficiency(db.Model):
    """Character proficiencies"""
    __tablename__= "proficiencies"
    id = db.Column(db.Integer, primary_key=True)
    proficiency = db.Column(db.String(80), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("proficiencies", lazy=True))

class SkillProf(db.Model):
    """Character skill proficiencies."""
    __tablename__= "skill_profs"
    id = db.Column(db.Integer, primary_key=True)
    proficiency = db.Column(db.String(80), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete="CASCADE"), nullable=False)
    character = db.relationship('Character', backref=db.backref('skill_profs', lazy=True))


class Spell(db.Model):
    """Character spells."""
    __tablename__= "spells"
    id = db.Column(db.Integer, primary_key=True)
    spell = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete="CASCADE"), nullable=False)
    character = db.relationship('Character', backref=db.backref('spells', lazy=True))


class SpellSlots(db.Model):
    """Character spell slots."""
    __tablename__= "spell_slots"
    id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.Integer, nullable=False)
    max = db.Column(db.Integer, nullable=False)
    empty = db.Column(db.Integer, nullable=False)
    filled = db.Column(db.Integer, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete="CASCADE"), nullable=False)
    character = db.relationship('Character', backref=db.backref('spell_slots', lazy=True))

class Inventory(db.Model):
    """Items in characters' inventories."""
    __tablename__= "inventories"
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(80), nullable=False)
    weight = db.Column(db.Float, default=0)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete="CASCADE"), nullable=False)
    character = db.relationship('Character', backref=db.backref('inventories', lazy=True))

class Currency(db.Model):
    """Currency in characters' inventories."""
    __tablename__ = "currency"
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=0)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete="CASCADE"), nullable=False)
    character = db.relationship('Character', backref=db.backref('currency', lazy=True))

class Languages(db.Model):
    """Languages characters speak."""
    __tablename__= "languages"
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(80), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("languages", lazy=True))

    def __init__(self, language, character_id):
        self.language = language
        self.character_id = character_id


class Personality(db.Model):
    """Character personality traits."""
    __tablename__= "personality_traits"
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String(1000))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("personality", lazy=True))

    def __init__(self, trait, character_id):
        self.trait = trait
        self.character_id = character_id


class Ideals(db.Model):
    """Character ideals."""
    __tablename__= "ideals"
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String(1000))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("ideals", lazy=True))

    def __init__(self, trait, character_id):
        self.trait = trait
        self.character_id = character_id


class Bonds(db.Model):
    """Character bonds."""
    __tablename__= "bonds"
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String(1000))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("bonds", lazy=True))

    def __init__(self, trait, character_id):
        self.trait = trait
        self.character_id = character_id


class Flaws(db.Model):
    """Character flaws."""
    __tablename__= "flaws"
    id = db.Column(db.Integer, primary_key=True)
    trait = db.Column(db.String(1000))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("flaws", lazy=True))

    def __init__(self, trait, character_id):
        self.trait = trait
        self.character_id = character_id


class PhysicalTraits(db.Model):
    """Character physical traits."""
    __tablename__= "physical_traits"
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(100))
    age = db.Column(db.String(100))
    weight = db.Column(db.String(100))
    height = db.Column(db.String(100))
    eyes = db.Column(db.String(100))
    skin = db.Column(db.String(100))
    hair = db.Column(db.String(100))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("physical_traits", lazy=True))

class Notes(db.Model):
    """Character notes."""
    __tablename__= "notes"
    id = db.Column(db.Integer, primary_key=True)
    organizations = db.Column(db.String(1000))
    allies = db.Column(db.String(1000))
    enemies = db.Column(db.String(1000))
    backstory = db.Column(db.String(1000))
    other = db.Column(db.String(1000))
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character = db.relationship("Character", backref=db.backref("notes", lazy=True))
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length


class NewUserForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class EquipmentForm(FlaskForm):
    """Form to get equipment."""

    item = StringField("Search")
    options = SelectField("Items", coerce=str)


class MonsterForm(FlaskForm):
    """Form to get monsters."""

    monster = StringField("Search")
    options = SelectField("Monsters", coerce=str)


class SpellForm(FlaskForm):
    """Form to get spells."""

    spell = StringField("Search")
    options = SelectField("Monsters", coerce=str)


class RulesForm(FlaskForm):
    """Form to get rules."""

    rule = StringField("Search")
    options = SelectField("Monsters", coerce=str)


class RaceForm(FlaskForm):
    """Form to get races."""

    race = StringField("Search")
    options = SelectField("Races", coerce=str)


class ClassForm(FlaskForm):
    """Form to get classes."""

    char_class = StringField("search")
    options = SelectField("Classes", coerce=str)
    
class NewCharacterNameForm(FlaskForm):
    """Form to create a new character."""
    
    name = StringField("Character Name", validators=[DataRequired()])
    advancement_type = SelectField("Advancement Type", coerce=str)
    hp_type = SelectField(label="Hit Point Type", coerce=str, validators=[DataRequired()])
    encumberance = SelectField(label="Encumberance Type", coerce=bool, validators=[DataRequired()])
    coin_weight = SelectField(label="Apply weight to currency?", coerce=bool)
    
    def fill(self):
        
        self.advancement_type.choices = [('choose', '-Choose Advancement Type-'), ('milestone', 'Milestone'), ('xp', 'Experience')]
        self.hp_type.choices = [('choose', '-Choose HP Type-'), ('fixed', "Fixed"), ('manual', 'Manual')]
        self.encumberance.choices = [('choose', '-Choose Encumberance Type-'), (True, "Use Encumberance"), (False, "No Encumberance")]
        self.coin_weight.choices = [('choose', '-Choose Weighted Coin-'), (False, 'No'), (True, 'Yes')]
    
class NewCharacterRaceForm(FlaskForm):
    """Form to choose a character's race."""
    
    races = SelectField("Choose a race", coerce=str)
    
class NewCharacterClassForm(FlaskForm):
    """Form to choose a character's class."""
    
    classes=SelectField("Choose a class", coerce=str)
    
class NewCharacterProficienciesForm(FlaskForm):
    profs1 = SelectField("1st Proficiency", coerce=str)
    profs2 = SelectField("2nd Proficiency", coerce=str)

class AbilityScoresInputTypeForm(FlaskForm):
    """Form for the method to choose ability scores."""
    scores = SelectField("", coerce=str)
    
    def fill(self):
        self.scores.choices = [('standard', "Standard Array"),
                               ('manual', "Manual/Rolled"),
                               ('points', "Point Buy")]


class AbilityScoresFormPointsOrArray(FlaskForm):
    """Form to choose abilities via point system."""
    strength = SelectField("STRENGTH", coerce=str)
    dexterity = SelectField("DEXTERITY", coerce=str)
    constitution = SelectField("CONSTITUTION", coerce=str)
    intelligence = SelectField("INTELLIGENCE", coerce=str)
    widsom = SelectField("WISDOM", coerce=str)
    charisma = SelectField("CHARISMA", coerce=str)
    
class AbilityScoresFormManualOrRolled(FlaskForm):
    """Form to choose abilities via point system."""
    strength = IntegerField("STRENGTH")
    dexterity = IntegerField("DEXTERITY", validators=[DataRequired()])
    constitution = IntegerField("CONSTITUTION", validators=[DataRequired()])
    intelligence = IntegerField("INTELLIGENCE", validators=[DataRequired()])
    widsom = IntegerField("WISDOM", validators=[DataRequired()])
    charisma = IntegerField("CHARISMA", validators=[DataRequired()])

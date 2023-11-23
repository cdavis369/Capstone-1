import json
from flask import Flask, redirect, render_template, flash, g, session, request, jsonify
from backgrounds import LIFESTYLE
#from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, Character, User, Proficiency, Currency, Inventory, Languages, Personality, Ideals, Bonds, Flaws, PhysicalTraits, Notes
from forms import *
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://eyflhgtm:thpH-f-6SbdXIZ2IhBeqpWKGBujvYFbH@bubble.db.elephantsql.com/eyflhgtm'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dnd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "MYFIRSTCAPSTONEPROJECT"
#debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

BASE_URL = "https://www.dnd5eapi.co/api"
with app.app_context():
  connect_db(app)
  db.create_all()
CURR_USER_KEY = "curr_user"

@app.before_request
def add_user_to_g():
  """Add current user to Flask global if logged in."""
  if CURR_USER_KEY in session:
    g.user = User.query.get(session[CURR_USER_KEY])
    if 'character_id' in session:
      g.character = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
    else:
      g.character = None
  else:
    g.user = None
    
def do_login(user):
  """Log in user."""
  session[CURR_USER_KEY] = user.id

  
def do_logout():
  """Logout user."""
  if CURR_USER_KEY in session:
    del session[CURR_USER_KEY]

    
@app.route('/register', methods=["GET", "POST"])
def register():
  """Handle registration of new user. 
  Create new user and add to database. Redirect to home page.
  If invalid form input or username taken, flash message
  and show submitted form."""
  
  form = NewUserForm()
  
  if form.validate_on_submit():
    try:
      user = User.register(username=form.username.data, password=form.password.data)
      db.session.commit()
    except IntegrityError:
      flash("Username already taken", "danger")
      return render_template('users/register.html', form=form)
    do_login(user)
    return redirect('/')
  else:
    return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def user_login():
  """Handle user login."""
  
  form = LoginForm()

  if form.validate_on_submit():
    user = User.authenticate(form.username.data, form.password.data)
    # print(f"======================================={user}")
    if user:
      do_login(user)
      flash(f"Welcome back, {user.username}.", "success")
      return redirect("/")
    else:
      flash("Invalid username and/or password.", "danger")
  
  return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
  """Handle user logout."""
  do_logout()
  flash("You have successfully signed out.", "success")
  return redirect('/')

@app.route('/', methods=["GET", "POST"])
def index():
  """Homepage"""
  if 'character_id' in session:
    del session['character_id']
    g.character = None
  form = EquipmentForm()
  response = requests.get(f"{BASE_URL}/equipment")
  items = response.json()
  form.options.choices = [(item['index'], item['name']) for item in items['results']]
  char_data = []
  if g.user:
    characters = Character.query.filter_by(user_id=g.user.id)
    
    for character in characters:
      char_data.append({'char_name':character.name, 'char_id':character.id})

  if form.validate_on_submit():
    search = form.item.data
    if not search:
      search = form.options.data
    response = requests.get(f"{BASE_URL}/equipment/{search}")
    r = response.json()
    return render_template("index.html", form=form, char_data=char_data, result=r)
  else:
    return render_template("index.html", form=form, char_data=char_data)
  
@app.route('/new-character', methods=["GET", "POST"])
def new_character():
  """Provide first form for a new character.
     name - hp/xp type - encumberance - coin weight."""
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  char = ""
  form = NewCharacterNameForm()
  
  if 'character_id' in session:
    char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
    form = NewCharacterNameForm(obj=char)
    
  form.fill()
  if form.validate_on_submit():
    for field in form:
      if field.data == 'choose':
        flash("All fields required.", "danger")
        return render_template("/characters/new.html", form=form)
    if 'character_id' in session:
      char.name = form.name.data
      char.advancement_type = form.advancement_type.data
      char.hp_type = form.hp_type.data
      char.encumberance = form.encumberance.data
      char.coin_weight = form.coin_weight.data
    else:
      char = Character(user_id=session[CURR_USER_KEY],
                                name=form.name.data,
                                advancement_type=form.advancement_type.data,
                                hp_type=form.hp_type.data,
                                encumbrance=form.encumberance.data,
                                coin_weight=form.coin_weight.data,
                                do_next = "race",
                                level=1)
    char.name_completed = True
    db.session.add(char)
    db.session.commit()
    session['character_id'] = char.id
    # print(f"===============================================\nCHAR ID:\n{session['character_id']}")
    return redirect("/new-character-race")
  
  return render_template("/characters/new.html", form=form)

@app.route('/new-character-race', methods=["GET", "POST"])
def new_character_race():
  """Show race options for new character."""
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  form = NewCharacterRaceForm()
  
  response = requests.get(f"{BASE_URL}/races")
  r = response.json()
  races = [('choose', '-Choose Your Race-')]
  
  if g.character.race_completed:
    races[0] = (g.character.race, g.character.race.capitalize())

  for race in r['results']:
    if race['index'] == g.character.race:
      continue
    races.append((race['index'], race['name']))


  form.races.choices = races
  
  if form.validate_on_submit():
    race = form.races.data
    if race == 'choose':
      flash("Choose your race.", "danger")
      return render_template("/characters/new.html", form=form) 
    char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
    char.race = form.races.data
    char.do_next = "class"
    char.race_completed = True
    db.session.commit()
    return redirect(f"/characters/new/race/{race}")
  
  return render_template("/characters/new.html", form=form) 

@app.route('/new-character-class', methods=["GET", "POST"])
def new_character_class():
  """ Show class options for new character."""
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  form = NewCharacterClassForm()
  response = requests.get(f" {BASE_URL}/classes")
  r = response.json()
  classes = [('choose', '-Choose Your Class-')]
  
  if g.character.character_class_completed:
    classes[0] = (g.character.character_class, g.character.character_class.capitalize())
  
  for char_class in r['results']:
    if char_class['index'] == g.character.character_class:
      continue
    classes.append((char_class['index'], char_class['name']))

  form.classes.choices = classes
  if form.validate_on_submit():
    character_class = form.classes.data
    if character_class == 'choose':
      flash("Choose your class.", "danger")
    char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
    char.character_class = character_class
    char.character_class_completed = True
    char.do_next = "proficiencies"
    db.session.commit()
    return redirect(f"/characters/new/class/{character_class}/proficiencies")
  
  return render_template("characters/new.html", form=form)

@app.route('/characters/new/race/<race>')
def show_race_details(race):
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  response = requests.get(f"{BASE_URL}/races/{race}")
  race_details = response.json()
  return render_template("/characters/race.html", race_details=race_details)

@app.route('/characters/new/class/<char_class>/proficiencies', methods=["GET", "POST"])
def show_class_details(char_class):
  if CURR_USER_KEY not in session or 'character_id' not in session:
    return redirect("/")
  
  response = requests.get(f"{BASE_URL}/classes/{char_class}")
  class_details = response.json()
  
  if request.method == 'POST':
    new_profs = []
    for index, prof in enumerate(class_details['proficiency_choices']):
      for j in range(prof['choose']):
        value = request.form.get(f"{index + 1}-{j}")
        if value == "-Choose-":
          flash("All proficiencies required.", "danger")
          return render_template('/characters/class.html', class_details=class_details)
        elif value in new_profs:
          flash("Cannot have duplicate proficiencies", "danger")
          return render_template('/characters/class.html', class_details=class_details)
        else:
          new_profs.append(value)
    char_profs = Proficiency.query.filter_by(character_id = session['character_id']).all()
    if len(char_profs) > 0:
      Proficiency.query.filter_by(character_id = session['character_id']).delete()
    # print(char_profs)

    for prof in new_profs:
      new_prof = Proficiency(proficiency = prof, character_id = session['character_id'], user_id = g.user.id)
      db.session.add(new_prof)
    char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
    char.do_next = "abilities"
    char.proficiencies_completed = True
    db.session.commit()
  
    return redirect('/characters/new/ability-scores')
  
  if g.character.proficiencies_completed:
    current_profs = Proficiency.query.filter_by(user_id=g.user.id, character_id=g.character.id)
    char_profs = [prof.proficiency for prof in current_profs]
    # print(char_profs)
    return render_template('/characters/class.html', class_details=class_details, current_profs=char_profs)
  
  return render_template('/characters/class.html', class_details=class_details)
    
@app.route('/characters/new/ability-scores', methods=["GET", "POST"])
def get_ability_scores_form():
  """Form to fill ability scores with race modifiers."""
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
  race = char.race
  response = requests.get(f"{BASE_URL}/races/{race}")
  race_details = response.json()
  ability_bonuses = race_details['ability_bonuses']
  bonuses = {ab['ability_score']['index']:ab['bonus'] for ab in ability_bonuses}
  
  if request.method == 'POST':
    ability_scores = request.get_json()
    char.strength = ability_scores['str']
    char.dexterity = ability_scores['dex']
    char.constitution = ability_scores['con']
    char.intelligence = ability_scores['int']
    char.wisdom = ability_scores['wis']
    char.charisma = ability_scores['cha']
    char.do_next = 'description'
    char.abilities_completed = True
    db.session.commit()
    # print(f"============================================{ability_scores}")
    return jsonify(success=True)

  return render_template("characters/abilities.html", bonuses=bonuses)
        
@app.route('/characters/new/description', methods=["GET", "POST"])
def get_character_description_form():
  """Form to provide physical character details and more."""
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
  error = ("============================================\n" +
           "Unable to retrieve general data from D&D 5e API -> ")
  char_data  = {}
  
  try:
    response = requests.get(f"{BASE_URL}/languages")
    char_data['languages'] = response.json()
  except:
    print(error + "languages")
  try:
    response = requests.get(f"{BASE_URL}/equipment-categories/artisans-tools")
    char_data['artisans_tools'] = response.json()
  except:
    print(error + "artisans_tools")
  try:
    if not hasattr(g, 'background'):
      response = requests.get(f"{BASE_URL}/backgrounds/acolyte")
      char_data['background'] = response.json()
      char_data['background_info'] = "You have spent your life in the service of a temple to a specific god or pantheon of gods. You act as an intermediary between the realm of the holy and the mortal world, performing sacred rites and offering sacrifices in order to conduct worshipers into the presence of the divine. You are not necessarily a cleric — performing sacred rites is not the same thing as channeling divine power. Choose a god, a pantheon of gods, or some other quasi-divine being, and work with your DM to detail the nature of your religious service. The Gods of the Multiverse section contains a sample pantheon, from the Forgotten Realms setting. Were you a lesser functionary in a temple, raised from childhood to assist the priests in the sacred rites? Or were you a high priest who suddenly experienced a call to serve your god in a different way? Perhaps you were the leader of a small cult outside of any established temple structure, or even an occult group that served a fiendish master that you now deny."
  except:
    print(error + "background")
  try:
    response = requests.get(f"{BASE_URL}/alignments")
    char_data['alignments'] = response.json()
  except:
    print(error + "alignments")
  try:
    response = requests.get(f"{BASE_URL}/races/{char.race}")
    char_data['race'] = response.json()
    # print(char_data['race'])
  except:
    print(error + "race")
  try:
    response = requests.get(f"{BASE_URL}/classes/{char.character_class}")
    char_data['class'] = response.json()
  except:
    print(error + "class")
    
  if request.method == "POST":
    details = request.get_json()
    languages = details['languages'].split(",")
    
    if g.character.description_completed:
      Languages.query.filter_by(character_id=char.id).delete()
      
      physicals_traits = PhysicalTraits.query.filter_by(character_id=char.id).first()
      physicals_traits.gender = details['gender']
      physicals_traits.age = details['age']
      physicals_traits.weight = details['weight']
      physicals_traits.height = details['height']
      physicals_traits.eyes = details['eyes']
      physicals_traits.skin = details['skin']
      physicals_traits.hair = details['hair']

      personality_trait = Personality.query.filter_by(character_id=char.id).first()
      personality_trait.trait = details['personality']['traits']

      ideals = Ideals.query.filter_by(character_id=char.id).first()
      ideals.trait=details['ideals']

      bonds = Bonds.query.filter_by(character_id=char.id).first()
      bonds.trait=details['bonds']

      flaws = Flaws.query.filter_by(character_id=char.id).first()
      flaws.trait = details['flaws']

      notes = Notes.query.filter_by(character_id=char.id).first()
      notes.organizations = details['organizations']
      notes.allies = details['allies']
      notes.enemies = details['enemies']
      notes.backstory = details['backstory']
      notes.other = details['other']
    else:
      physicals_traits = PhysicalTraits(gender=details['gender'],
                                        age=details['age'],
                                        weight=details['weight'],
                                        height=details['height'],
                                        eyes=details['eyes'],
                                        skin=details['skin'],
                                        hair=details['hair'],
                                        character_id=char.id,)
      db.session.add(physicals_traits)    

      personality_trait = Personality(trait=details['personality']['traits'],
                                    character_id=char.id)
      db.session.add(personality_trait)
      
      ideals = Ideals(trait=details["ideals"], character_id=char.id)
      db.session.add(ideals)
      
      bonds = Bonds(trait=details["bonds"], character_id=char.id)
      db.session.add(bonds)
      
      flaws = Flaws(trait=details["flaws"], character_id=char.id)
      db.session.add(flaws)
      
      notes = Notes(organizations=details['organizations'],
                    allies=details['allies'],
                    enemies=details['enemies'],
                    backstory=details['backstory'],
                    other=details['other'],
                    character_id=char.id)
      db.session.add(notes)


    for language in char_data['race']['languages']:
      languages.append(language['name'])

    for language in languages:
      lang = language.strip()
      new_lang = Languages(language=lang, character_id=char.id)
      db.session.add(new_lang)
      
    char.lifestyle = details['lifestyle']
    char.alignment = details['alignment']
    char.faith = details['faith']
    char.do_next = 'inventory'
    char.description_completed = True
    db.session.commit()
    return jsonify(success=True)

  if g.character.description_completed:
    physicals_traits = PhysicalTraits.query.filter_by(character_id=char.id).first()
    personality_trait = Personality.query.filter_by(character_id=char.id).first()
    ideals = Ideals.query.filter_by(character_id=char.id).first()
    bonds = Bonds.query.filter_by(character_id=char.id).first()
    flaws = Flaws.query.filter_by(character_id=char.id).first()
    notes = Notes.query.filter_by(character_id=char.id).first()
    return render_template("characters/description.html", 
                           name=char.name,
                           char_data=char_data,
                           lifestyle=LIFESTYLE,
                           physicals_traits=physicals_traits,
                           personality_trait=personality_trait,
                           ideals=ideals,
                           bonds=bonds,
                           flaws=flaws,
                           notes=notes)

  return render_template("characters/description.html", 
                         name=char.name,
                         char_data=char_data,
                         lifestyle=LIFESTYLE)

@app.route('/lifestyles/desc/<lifestyle>')
def get_lifestyle_description(lifestyle):
  for i in range(len(LIFESTYLE)):
    if LIFESTYLE[i]['name'] == lifestyle:
      return jsonify(success=True, desc=LIFESTYLE[i]['desc'])
  return jsonify(success=False)

@app.route('/characters/new/inventory', methods=["GET", "POST"])
def show_inventory_options():
  if CURR_USER_KEY not in session:
    return redirect("/")
  char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=session['character_id']).first()
  
  if request.method == "POST":
    data = request.get_json()
    if data['inventory_type'] == 'gold':
      inventory = Inventory.query.filter_by(character_id=char.id).all()
      if inventory:
        for item in inventory:
          db.session.delete(item)
      amount = data['quantity']
      weight = float(amount) * 0.02
      gold = Currency.query.filter_by(character_id=char.id).first()
      if gold:
        gold.amount = amount
        gold.weight = weight
      else:
        gold = Currency(currency = 'gp',
                          amount = amount,
                          weight = weight, 
                          character_id = char.id)
        db.session.add(gold)
    else:
      gold = Currency.query.filter_by(character_id=char.id).first()
      print(gold)
      if gold:
        db.session.delete(gold)
      inventory = Inventory.query.filter_by(character_id=char.id).all()
      if inventory:
        for item in inventory:
          db.session.delete(item)
      equipment = data['equipment'].split(',')
      for item in equipment:
        response = requests.get(f"{BASE_URL}/equipment/{item}")
        r = response.json()
        new_item = Inventory(item=item, character_id=char.id)
        if 'weight' in r:
          new_item.weight = r['weight']
        db.session.add(new_item)
    char.inventory_completed = True
    char.completed = True
    db.session.commit()
    return jsonify(success=True)

  
  response = requests.get(f"{BASE_URL}/classes/{char.character_class}")
  char_class = response.json()
  response = requests.get(f"{BASE_URL}/races/{char.race}")
  race = response.json()
  equipment_choices = []
  for i in range(len(char_class['starting_equipment_options'])):
    option = {'desc': char_class['starting_equipment_options'][i]['desc']}
    option['choose'] = char_class["starting_equipment_options"][i]["choose"]
    option['from'] = char_class["starting_equipment_options"][i]["from"]
    equipment_choices.append(option)
    
  if char.inventory_completed:
    gold = gold = Currency.query.filter_by(character_id=char.id).first()
    inventory = {}
    if gold:
      inventory['type'] = 'gold'
      inventory['gold'] = gold
    else:
      equipment = Inventory.query.filter_by(character_id=char.id).all()
      inventory['type'] = 'equipment'
      inventory['equipment'] = equipment
    return render_template("characters/inventory.html", 
                         char_class=char_class,
                         race=race,
                         equipment_choices=equipment_choices, 
                         inventory=inventory) 
  return render_template("characters/inventory.html", 
                         char_class=char_class,
                         race=race,
                         equipment_choices=equipment_choices)
  
@app.route('/users/characters/<int:character_id>')
def get_user_character(character_id):
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=character_id).first()
  if char:
    session['character_id'] = character_id

  if char.completed == False:
    if char.do_next == 'name':
      return redirect('/new-character')
    elif char.do_next == 'race':
      return redirect('/new-character-race')
    elif char.do_next == 'class':
      return redirect('/new-character-class')
    elif char.do_next == 'proficiencies':
      return redirect(f'/characters/new/class/{char.character_class}/proficiencies')
    elif char.do_next == 'abilities':
      return redirect('/characters/new/ability-scores')
    elif char.do_next == 'description':
      return redirect('/characters/new/description')
    elif char.do_next == 'inventory':
      return redirect('/characters/new/inventory')
  else:
    return redirect('/new-character')
    
@app.route('/users/characters/delete/<int:character_id>')
def delete_character(character_id):
  if CURR_USER_KEY not in session:
    return redirect("/")
  
  char = Character.query.filter_by(user_id=session[CURR_USER_KEY], id=character_id).first()
  db.session.delete(char)
  db.session.commit()
  return redirect('/')

    

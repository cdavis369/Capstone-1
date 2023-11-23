
function abilitiesRoll(ability) {
  $formInput = $(`#result-${ability}`);
  const rolls = [];
  // console.log(ability)
  while (rolls.length < 4) {
    roll = Math.floor(Math.random() * 6) + 1;
    // console.log("ROLL: " + roll);
    rolls.push(roll);
  }
  // console.log(rolls);
  rolls.sort().reverse();
  // console.log(rolls);
  let total = 0;
  
  for (let i = 0; i < 4; i++) {
    $rollDisplay = $(`#ability-roll-proccess-${ability}-${i}`);
    console.log($rollDisplay)
    $rollDisplay.html(i)

    if (i < 3)
      total += rolls[i];
    
  }
  // console.log(total);
  
  $formInput.val(total);
}

function rollAllAbilities() {
  abilities = ["str", "dex", "con", "int", "wis", "cha"]
  for (i in abilities) 
    roll = abilitiesRoll(abilities[i]);
}

function addAbilitiesRolls() {
  let $rollResult = $('.roll-result');
  $rollResult.each(function() {
    const ability = this.name.slice(7,);
    const score = parseInt($(this).val());
    if (score) {
      const bonus = parseInt($(`#${ability}-calc-bonus`).text());
      const total = score + bonus;
      $(`#input-${ability}`).val(total);
      $(`#${ability}-calc-total`).text(total);
    }

  });
}

async function submitAbilities() {
  const formData = new FormData();
  $abilityScores = $('.abilities-final');
  let complete = true;
  $abilityScores.each(function() {
    const ability = this.id.slice(6,);
    const score = this.value;
    if (score === "")
      complete = false;
    formData.append(ability, score)
  })
  if (complete) {
    try {
      response = await axios({
        method: "POST",
        url: "/characters/new/ability-scores",
        data: formData,
        headers: {'Content-Type': 'application/json'}
      });
      location.href = "/characters/new/description";
    }
    catch (error) {
      // console.log(error);
      alert(error);
    }
  }
  else
    alert("All abilities require a value.");
}

function addRacialBonus(ability) {
  score_input = $(`#input-${ability}`);
  score = parseInt(score_input.val());
  score_input.val(0)
  bonus = parseInt($(`#${ability}-calc-bonus`).text());
  total = score + bonus;
  $(`#input-${ability}`).val(total);
}

async function getAlignmentDetails(index) {
  try {
    response = await axios({
      method: "GET",
      url: `https://www.dnd5eapi.co/api/alignments/${index}`
    });
    // data = JSON.parse(response['data'])
    const desc = response.data.desc;
    $('#alignment-desc').text(desc);
  }
  catch(error) {
    // console.log(error);
    alert(error);
  }

}

$('.abilities-final').change(function(evt) {
  const ability = evt.target.name;
  score_input = $(`#input-${ability}`);
  if (score_input.val() < 0 || score_input.val() > 20) {
    score_input.val('');
    alert("Abilities are from 0 through 20.")
  }
  addRacialBonus(ability);
});

async function getLifestyleDesc(lifestyle) {
  try {
    response = await axios({
      method: "GET",
      url: `/lifestyles/desc/${lifestyle}`
    });
    const result = response.data
    if (result['success']) {
      const desc = result['desc'];
      $('#lifestyle-desc').text(desc);
    }
  }
  catch(error) {
    alert(error);
  }
}

function addCharacteristic(id) {
  const traitID = id.slice(4,);
  const description = $(`#${traitID}`).text().replace(/^\s+/g, '').replace(/\s+$/g, '');
  const textId = `${traitID.slice(2,)}-text`;
  let text = $(`#${textId}`).text();

  if (!text.includes(description)) {
    $(`#${id}`).removeClass('btn-info');
    $(`#${id}`).addClass('btn-secondary');
    text += ` ${description}`
    $(`#${textId}`).text(`${text.replace(/^\s+/g, '').replace(/\s+$/g, '')}`)
  }
  else {
    $(`#${id}`).removeClass('btn-secondary');
    $(`#${id}`).addClass('btn-info');
    $(`#${textId}`).text(`${text.replace(description,'').replace(/^\s+/g, '').replace(/\s+$/g, '')}`)
  }
}

async function submitCharacterDetails() {
  const details = {'languages': ""};
  let langs = "";
  let errorMessage = "";
  let langError = false;
  const formData = new FormData();
  
  details['faith'] = $('#char-faith').val();

  $('.languages').each(function() {
    if ($(this).val() !== "-Choose a language-") {
      langs += `${$(this).val()}, `;
      details["languages"] = langs.slice(0, -2);
    }
    else 
      langError = true;
  });
  // console.log(details['languages']);
  $lifestyle = $('#char-lifestyle').val();

  if ($lifestyle === "-Choose lifestyle-")
    errorMessage = "Lifestyle choice is required.";
  else
    details['lifestyle'] = $lifestyle;

  $alignment = $('#char-alignment').val();

  if ($alignment === "-Choose alignment-")
    errorMessage += " Alignment choice is required.";
  else
    details['alignment'] = $alignment;

  if (langError === true) 
    errorMessage += " All potential language options are required.";

  if (errorMessage === "") {
    $('.physical-details').each(function() {
      const detail = this.id.slice(5,);
      const desc = $(this).val();
      details[detail] = desc;
    });
  
    $('.char-traits').each(function() {
      const trait = this.id.slice(0, -5);
      const desc = $(this).val();
      details[trait] = desc;
    });
    
    Object.entries(details).forEach(function([key, value]) {
      formData.append(key, value);
    });
    
    try {
      response = await axios({
        method: "POST",
        url: "/characters/new/description",
        data: formData,
        headers: {'Content-Type': 'application/json'}
      });
      // console.log(response.data);
      location.href = "/characters/new/inventory"
    }
    catch (error) {
      alert(error);
    }
  }
  else {
    alert(errorMessage);
  }
}

async function addGoldToInventory(amount) {
  const formData = new FormData();
  const inventory = [];
  inventory['inventory_type'] = 'gold';
  inventory['quantity'] = amount;
  Object.entries(inventory).forEach(function([key, value]) {
    formData.append(key, value);
  });

  try {
    response = await axios({
      method: "POST",
      url: "/characters/new/inventory",
      data: formData,
      headers: {'Content-Type': 'application/json'}
    });
  }
  catch (error) {
    alert(error);
  }
  location.href = "/";
}

async function addEquipmentToInventory(equipment) {
  const formData = new FormData();
  const inventory = [];
  inventory['inventory_type'] = 'equipment';
  inventory['equipment'] = [];
  equipment.each(function() { 
    inventory['equipment'].push(this.value)
  });
  // console.log(inventory['equipment'])
  Object.entries(inventory).forEach(function([key, value]) {
    formData.append(key, value);
  });

  try {
    response = await axios({
      method: "POST",
      url: "/characters/new/inventory",
      data: formData,
      headers: {'Content-Type': 'application/json'}
    });
  }
  catch (error) {
    alert(error);
  }
  location.href = "/";
}

$('.add-gold').click(function() {
  const startingGold = $('#starting-gold-result').text();
  const amount = startingGold.substring(0, startingGold.length - 3);
  if (amount === "0")
    alert("Starting gold or equipment required.");
  else 
    addGoldToInventory(amount);
  }
);

$('.add-equipment').click(function() {
  $equipment = $('.starting-equipment-option');
  var error = false;
  $equipment.each(function() {
    if (this.value == '-Choose-')
      error = true;
  });
  if (error == true)
  alert("All equipment must be chosen.");
  else
    addEquipmentToInventory($equipment);
});

$('#add-rolls').click(function(evt) {
  evt.preventDefault();
  addAbilitiesRolls();
});

$('#roll-all-abilities').click(function(evt){
  evt.preventDefault();
  rollAllAbilities();
});

$('.abilities-roll').click((evt) => {
  ability = evt.target.id.slice(5,)
  abilitiesRoll(ability);
});

$('#btn-submit-abilities').click(submitAbilities);

$('#char-alignment').change(function() {
  const alignment = this.value;
  if (alignment !== '-Choose alignment-')
    getAlignmentDetails(alignment);
  else
  $('#alignment-desc').text("");
});

$('#char-lifestyle').change(function() {
  const lifestyle = this.value;
  if (lifestyle !== '-Choose lifestyle-')
    getLifestyleDesc(lifestyle);
  else {
    $('#lifestyle-desc').text("");
  }
});

$('.btn-add-characteristic').click(function(evt) {
  evt.preventDefault();
  addCharacteristic(this.id);
});

$('#btn-submit-details').click(function (evt) {
  evt.preventDefault();
  submitCharacterDetails();
});

$('.inventory-choice').click(function () {
  choice = this.id.slice(0,-7);
  // console.log(choice);
});

$('#starting-gold-option').change(function() {
  const selected = $('#starting-gold-option').val();
  $('#starting-gold-result').text(selected*10+" gp");
})

$('#random-gold-roll').click(function() {
  roll = Math.floor(Math.random() * 16) + 5;
  $('#starting-gold-option').val(roll).change()
  $('#starting-gold-result').text(roll*10+" gp");

});

$('#gold-option').click(function() {
  $('#starting-gold').show()
  $('#starting-equipment').hide()
});

$('#equipment-option').click(function() {
  $('#starting-equipment').show()
  $('#starting-gold').hide()
});

from flask import Flask, render_template_string, request, redirect, url_for, session
# from pyngrok import ngrok  # <-- SUPPRIME CETTE LIGNE
import hashlib, json, os, random

app = Flask(__name__)
app.secret_key = "pokemon_secret_CHANGE_IN_PROD"

# ================== CONFIG ==================
USERS_FILE = "pokemon_users.json"
SAVES_DIR = "pokemon_saves"
os.makedirs(SAVES_DIR, exist_ok=True)

# ================== DATA ==================
bosses = [
    {"nom": "Nerkael", "pokemon": ["Pikachu", "Évoli"], "recompense": 150, "niveau": 3},
    {"nom": "Ignivor", "pokemon": ["Lucario", "Dracolosse"], "recompense": 300, "niveau": 5},
    {"nom": "Aquarion", "pokemon": ["Metalosse", "Tyranocif"], "recompense": 500, "niveau": 8},
    {"nom": "Terragon", "pokemon": ["Dracaufeu", "Mew"], "recompense": 1000, "niveau": 12},
    {"nom": "Pyrodraco", "pokemon": ["Dracaufeu", "Mew"], "recompense": 1000000, "niveau": 20}
]

pokemon_stats = {
    "Pikachu": {"pv": 100, "attaque": 30, "rarete": "Commun"},
    "Évoli": {"pv": 120, "attaque": 25, "rarete": "Commun"},
    "Lucario": {"pv": 130, "attaque": 35, "rarete": "Rare"},
    "Dracolosse": {"pv": 150, "attaque": 40, "rarete": "Rare"},
    "Metalosse": {"pv": 140, "attaque": 45, "rarete": "Épique"},
    "Tyranocif": {"pv": 150, "attaque": 50, "rarete": "Épique"},
    "Dracaufeu": {"pv": 160, "attaque": 45, "rarete": "Mythique"},
    "Mew": {"pv": 170, "attaque": 50, "rarete": "Mythique"}
}

PRIX_VENTE = {"Commun": 40, "Rare": 120, "Épique": 300, "Mythique": 800}
BONUS_ATK = {"Commun": 0, "Rare": 5, "Épique": 12, "Mythique": 25}
MAX_EQUIPE = 6

LANGUES = {
    "fr": {"welcome": "Salut {nom}", "login": "Se connecter", "register": "Créer un compte", 
           "menu": "Menu", "fight": "⚔️ Combattre", "booster": "🎁 Booster (50€)", 
           "collection": "📋 Collection", "sell": "💸 Vendre", "heal_team": "❤️ Soigner (30€)",
           "save": "💾 Sauvegarder", "quit": "🚪 Quitter", "back": "← Retour",
           "money": "Argent", "boss_progress": "Boss vaincus", "choose_pokemon": "Choisis ton Pokémon",
           "attack": "Attaquer", "heal": "Soigner", "victory": "🏆 VICTOIRE", "defeat": "💀 Défaite"},
    "en": {"welcome": "Hello {nom}", "login": "Login", "register": "Create account",
           "menu": "Menu", "fight": "⚔️ Fight", "booster": "🎁 Booster (50€)",
           "collection": "📋 Collection", "sell": "💸 Sell", "heal_team": "❤️ Heal (30€)",
           "save": "💾 Save", "quit": "🚪 Quit", "back": "← Back",
           "money": "Money", "boss_progress": "Bosses defeated", "choose_pokemon": "Choose Pokémon",
           "attack": "Attack", "heal": "Heal", "victory": "🏆 VICTORY", "defeat": "💀 Defeat"},
    "ru": {"welcome": "Привет {nom}", "login": "Войти", "register": "Создать аккаунт",
           "menu": "Меню", "fight": "⚔️ Сразиться", "booster": "🎁 Бустер (50€)",
           "collection": "📋 Коллекция", "sell": "💸 Продать", "heal_team": "❤️ Лечить (30€)",
           "save": "💾 Сохранить", "quit": "🚪 Выйти", "back": "← Назад",
           "money": "Деньги", "boss_progress": "Побеждено", "choose_pokemon": "Выбери покемона",
           "attack": "Атаковать", "heal": "Лечить", "victory": "🏆 ПОБЕДА", "defeat": "💀 Поражение"}
}

# ================== UTILS ==================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    return json.load(open(USERS_FILE, encoding='utf-8')) if os.path.exists(USERS_FILE) else {}

def save_users(u):
    json.dump(u, open(USERS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def load_game(user):
    f = os.path.join(SAVES_DIR, f"{user}.json")
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {"argent": 150, "collection": [], "boss_actuel": 0}

def save_game(user, data):
    json.dump(data, open(os.path.join(SAVES_DIR, f"{user}.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def get_state():
    if 'username' not in session or 'game_state' not in session:
        session['game_state'] = load_game(session.get('username', ''))
    return session['game_state']

def update_state(updates):
    state = get_state()
    state.update(updates)
    session['game_state'] = state
    session.modified = True

# ================== STYLES ==================
BASE_STYLE = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}
.container {
    max-width: 800px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
h1 { color: #667eea; margin-bottom: 20px; text-align: center; }
.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 15px 30px;
    font-size: 1.1em;
    border-radius: 10px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin: 5px;
    transition: transform 0.2s;
}
.btn:hover { transform: translateY(-3px); }
.btn-secondary { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat { text-align: center; margin: 20px 0; font-size: 1.3em; color: #555; }
.pokemon-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.health-bar {
    background: #ddd;
    height: 20px;
    border-radius: 10px;
    overflow: hidden;
    margin: 10px 0;
}
.health-fill {
    background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
    height: 100%;
    transition: width 0.3s;
}
input {
    width: 100%;
    padding: 15px;
    margin: 10px 0;
    border: 2px solid #ddd;
    border-radius: 10px;
    font-size: 1em;
}
.msg {
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
    font-weight: bold;
}
.msg-success { background: #d4edda; color: #155724; }
.msg-error { background: #f8d7da; color: #721c24; }
</style>
"""

# ================== ROUTES ==================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["lang"] = request.form["lang"]
        return redirect(url_for("login_page"))
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container" style="text-align:center;">
        <h1>🎮 Pokémon Game</h1>
        <p style="font-size:1.2em;margin:20px 0;">Choisir la langue / Choose language / Выбрать язык</p>
        <form method="post">
            <button class="btn" name="lang" value="fr">🇫🇷 FR</button>
            <button class="btn" name="lang" value="en">🇬🇧 EN</button>
            <button class="btn" name="lang" value="ru">🇷🇺 RU</button>
        </form>
    </div></body>
    """)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    msg = ""
    
    if request.method == "POST":
        user, pw = request.form["username"], request.form["password"]
        users = load_users()
        if user in users and users[user]["password"] == hash_pw(pw):
            session['username'] = user
            session['game_state'] = load_game(user)
            return redirect(url_for("menu"))
        msg = "❌ Invalid credentials"
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>🎮 {{T['login']}}</h1>
        {% if msg %}<p class="msg msg-error">{{msg}}</p>{% endif %}
        <form method="post">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password" placeholder="Password" required>
            <button class="btn" type="submit">{{T['login']}}</button>
        </form>
        <a href="{{url_for('signup_page')}}"><button class="btn btn-secondary">{{T['register']}}</button></a>
    </div></body>
    """, T=T, msg=msg)

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    msg = ""
    
    if request.method == "POST":
        user, pw = request.form["username"], request.form["password"]
        users = load_users()
        if user in users:
            msg = "❌ User exists"
        else:
            users[user] = {"password": hash_pw(pw)}
            save_users(users)
            return redirect(url_for("login_page"))
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>📝 {{T['register']}}</h1>
        {% if msg %}<p class="msg msg-error">{{msg}}</p>{% endif %}
        <form method="post">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password" placeholder="Password" required>
            <button class="btn btn-secondary" type="submit">{{T['register']}}</button>
        </form>
    </div></body>
    """, T=T, msg=msg)

@app.route("/menu")
def menu():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    current_boss = bosses[state['boss_actuel']]['nom'] if state['boss_actuel'] < len(bosses) else "✅ Tous battus"
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>🎮 {{T['menu']}}</h1>
        <div class="stat">
            💰 {{state['argent']}}€ | 🏆 {{state['boss_actuel']}}/{{bosses|length}} | 📋 {{state['collection']|length}}/6
        </div>
        <p style="text-align:center;background:#f093fb;color:white;padding:10px;border-radius:10px;margin:20px 0;">
            🔥 Boss: {{current_boss}}
        </p>
        <div style="text-align:center;">
            <a href="{{url_for('fight')}}"><button class="btn">{{T['fight']}}</button></a>
            <a href="{{url_for('booster')}}"><button class="btn">{{T['booster']}}</button></a>
            <a href="{{url_for('collection_page')}}"><button class="btn">{{T['collection']}}</button></a>
            <a href="{{url_for('sell')}}"><button class="btn">{{T['sell']}}</button></a>
            <a href="{{url_for('heal_team')}}"><button class="btn">{{T['heal_team']}}</button></a>
            <a href="{{url_for('save')}}"><button class="btn">{{T['save']}}</button></a>
            <a href="{{url_for('quit')}}"><button class="btn btn-secondary">{{T['quit']}}</button></a>
        </div>
    </div></body>
    """, T=T, state=state, current_boss=current_boss, bosses=bosses)

@app.route("/booster", methods=["GET", "POST"])
def booster():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    msg = ""
    new_pkm = None
    
    if request.method == "POST":
        if state['argent'] < 50:
            msg = ("❌ Pas assez d'argent" if lang == "fr" else "❌ Not enough money" if lang == "en" else "❌ Недостаточно")
        elif len(state['collection']) >= MAX_EQUIPE:
            msg = ("⚠️ Équipe pleine" if lang == "fr" else "⚠️ Team full" if lang == "en" else "⚠️ Команда полна")
        else:
            state['argent'] -= 50
            t = random.randint(1, 100)
            if t <= 50:
                nom = random.choice(["Pikachu", "Évoli"])
            elif t <= 70:
                nom = random.choice(["Lucario", "Dracolosse"])
            elif t <= 90:
                nom = random.choice(["Metalosse", "Tyranocif"])
            elif t <= 98:
                nom = "Dracaufeu"
            else:
                nom = "Mew"
            
            stats = pokemon_stats[nom]
            new_pkm = {"nom": nom, "pv": stats["pv"], "pv_max": stats["pv"], 
                      "attaque": stats["attaque"] + BONUS_ATK[stats["rarete"]], 
                      "rarete": stats["rarete"], "niveau": 1, "xp": 0}
            state['collection'].append(new_pkm)
            update_state(state)
            msg = f"✨ {T.get('got_pokemon', 'Obtenu')}: {nom} ({stats['rarete']}) !"
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>🎁 {{T['booster']}}</h1>
        <div class="stat">💰 {{state['argent']}}€</div>
        {% if msg %}<p class="msg {{'msg-success' if new_pkm else 'msg-error'}}">{{msg}}</p>{% endif %}
        {% if new_pkm %}
        <div class="pokemon-card" style="text-align:center;">
            <h2>{{new_pkm['nom']}}</h2>
            <p style="color:#667eea;font-weight:bold;">{{new_pkm['rarete']}} | Niv.{{new_pkm['niveau']}}</p>
            <p>❤️ {{new_pkm['pv']}} HP | ⚔️ {{new_pkm['attaque']}} ATK</p>
        </div>
        {% endif %}
        <form method="post" style="text-align:center;margin:20px 0;">
            <button class="btn" type="submit">Ouvrir booster (50€)</button>
        </form>
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, state=state, msg=msg, new_pkm=new_pkm)

@app.route("/collection")
def collection_page():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>📋 {{T['collection']}}</h1>
        {% if state['collection'] %}
            {% for p in state['collection'] %}
            <div class="pokemon-card">
                <h3>{{p['nom']}} <span style="color:#667eea;">Niv.{{p['niveau']}}</span></h3>
                <p style="color:#999;">{{p['rarete']}}</p>
                <div class="health-bar">
                    <div class="health-fill" style="width:{{(p['pv']/p['pv_max']*100)}}%;"></div>
                </div>
                <p>❤️ {{p['pv']}}/{{p['pv_max']}} HP | ⚔️ {{p['attaque']}} ATK | ✨ {{p['xp']}}/{{p['niveau']*100}} XP</p>
            </div>
            {% endfor %}
        {% else %}
            <p style="text-align:center;color:#999;margin:40px 0;">Aucun Pokémon</p>
        {% endif %}
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, state=state)

@app.route("/sell", methods=["GET", "POST"])
def sell():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    msg = ""
    
    if request.method == "POST" and state['collection']:
        idx = int(request.form["index"])
        pkm = state['collection'].pop(idx)
        prix = PRIX_VENTE[pkm['rarete']]
        state['argent'] += prix
        update_state(state)
        msg = f"💸 {pkm['nom']} vendu pour {prix}€"
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>💸 {{T['sell']}}</h1>
        <div class="stat">💰 {{state['argent']}}€</div>
        {% if msg %}<p class="msg msg-success">{{msg}}</p>{% endif %}
        {% if state['collection'] %}
            <form method="post">
                {% for i, p in enumerate(state['collection']) %}
                <div class="pokemon-card" style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <strong>{{p['nom']}}</strong> Niv.{{p['niveau']}} ({{p['rarete']}})
                    </div>
                    <button class="btn" name="index" value="{{i}}" type="submit">Vendre {{PRIX_VENTE[p['rarete']]}}€</button>
                </div>
                {% endfor %}
            </form>
        {% else %}
            <p style="text-align:center;color:#999;margin:40px 0;">Aucun Pokémon</p>
        {% endif %}
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, state=state, msg=msg, enumerate=enumerate, PRIX_VENTE=PRIX_VENTE)

@app.route("/heal_team", methods=["GET", "POST"])
def heal_team():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    msg = ""
    
    if request.method == "POST":
        if state['argent'] < 30:
            msg = "❌ Pas assez d'argent"
        else:
            state['argent'] -= 30
            for p in state['collection']:
                p['pv'] = p['pv_max']
            update_state(state)
            msg = "✨ Équipe soignée !"
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>❤️ {{T['heal_team']}}</h1>
        <div class="stat">💰 {{state['argent']}}€</div>
        {% if msg %}<p class="msg {{'msg-success' if '✨' in msg else 'msg-error'}}">{{msg}}</p>{% endif %}
        <form method="post" style="text-align:center;margin:20px 0;">
            <button class="btn" type="submit">Soigner l'équipe (30€)</button>
        </form>
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, state=state, msg=msg)

@app.route("/fight", methods=["GET", "POST"])
def fight():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    
    if state['boss_actuel'] >= len(bosses):
        return render_template_string(BASE_STYLE + """
        <body><div class="container">
            <h1>🎊 FÉLICITATIONS !</h1>
            <p style="text-align:center;font-size:1.5em;margin:40px 0;">Tous les boss sont vaincus !</p>
            <a href="{{url_for('menu')}}"><button class="btn">{{T['back']}}</button></a>
        </div></body>
        """, T=T)
    
    boss = bosses[state['boss_actuel']]
    available = [p for p in state['collection'] if p['pv'] > 0]
    
    if not available:
        return render_template_string(BASE_STYLE + """
        <body><div class="container">
            <h1>❌ Aucun Pokémon disponible</h1>
            <p style="text-align:center;margin:20px 0;">Soigne ton équipe avant de combattre !</p>
            <a href="{{url_for('menu')}}"><button class="btn">{{T['back']}}</button></a>
        </div></body>
        """, T=T)
    
    if request.method == "POST" and 'pokemon_idx' not in session:
        # on retient la place du Pokémon dans toute la collection (pas dans la liste des disponibles)
        session['pokemon_idx'] = state['collection'].index(available[int(request.form['pokemon_idx'])])
        session['boss_pokemon'] = random.choice(boss['pokemon'])
        stats = pokemon_stats[session['boss_pokemon']]
        session['boss_pv'] = stats['pv'] + (boss['niveau'] * 10)
        session['boss_pv_max'] = session['boss_pv']
        session['boss_atk'] = stats['attaque'] + (boss['niveau'] * 2)
        session['combat_log'] = []
        session.modified = True
        return redirect(url_for('fight_action'))
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>⚔️ Combattre {{boss['nom']}}</h1>
        <p style="text-align:center;margin:20px 0;font-size:1.2em;">Niveau {{boss['niveau']}} | Récompense: {{boss['recompense']}}€</p>
        <h2>{{T['choose_pokemon']}}</h2>
        <form method="post">
            {% for i, p in enumerate(available) %}
            <div class="pokemon-card" style="cursor:pointer;">
                <button class="btn" name="pokemon_idx" value="{{i}}" type="submit" style="width:100%;text-align:left;">
                    <strong>{{p['nom']}}</strong> Niv.{{p['niveau']}} | ❤️ {{p['pv']}}/{{p['pv_max']}} | ⚔️ {{p['attaque']}}
                </button>
            </div>
            {% endfor %}
        </form>
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, boss=boss, available=available, enumerate=enumerate)

@app.route("/fight_action", methods=["GET", "POST"])
def fight_action():
    if 'username' not in session or 'pokemon_idx' not in session:
        return redirect(url_for("fight"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    boss = bosses[state['boss_actuel']]
    pokemon = state['collection'][session['pokemon_idx']]
    
    msg = ""
    if request.method == "POST":
        action = request.form['action']
        log = session.get('combat_log', [])
        
        if action == "attack":
            dmg = random.randint(pokemon['attaque']-5, pokemon['attaque']+5)
            if random.randint(1,100) <= 15:
                dmg = int(dmg * 1.5)
                log.append(f"💥 {pokemon['nom']} CRITIQUE: -{dmg}")
            else:
                log.append(f"⚔️ {pokemon['nom']}: -{dmg}")
            session['boss_pv'] -= dmg
        elif action == "heal":
            heal = int(pokemon['pv_max'] * 0.45)
            pokemon['pv'] = min(pokemon['pv_max'], pokemon['pv'] + heal)
            log.append(f"💚 {pokemon['nom']}: +{heal} HP")
        
        if session['boss_pv'] > 0:
            if random.randint(1,100) <= 20:
                heal = int(session['boss_pv_max'] * 0.45)
                session['boss_pv'] = min(session['boss_pv_max'], session['boss_pv'] + heal)
                log.append(f"💚 Boss: +{heal} HP")
            else:
                dmg = random.randint(session['boss_atk']-5, session['boss_atk']+5)
                if random.randint(1,100) <= 15:
                    dmg = int(dmg * 1.5)
                    log.append(f"⚡ Boss CRITIQUE: -{dmg}")
                else:
                    log.append(f"🔥 Boss: -{dmg}")
                pokemon['pv'] -= dmg
        
        session['combat_log'] = log[-5:]
        session.modified = True
        update_state(state)
        
        if pokemon['pv'] <= 0 or session['boss_pv'] <= 0:
            return redirect(url_for('fight_result'))
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>⚔️ Combat vs {{boss['nom']}}</h1>
        <div class="pokemon-card">
            <h3>🔥 Boss: {{session['boss_pokemon']}} Niv.{{boss['niveau']}}</h3>
            <div class="health-bar">
                <div class="health-fill" style="width:{{(session['boss_pv']/session['boss_pv_max']*100)}}%;"></div>
            </div>
            <p>❤️ {{session['boss_pv']}}/{{session['boss_pv_max']}} HP</p>
        </div>
        <div class="pokemon-card">
            <h3>💙 {{pokemon['nom']}} Niv.{{pokemon['niveau']}}</h3>
            <div class="health-bar">
                <div class="health-fill" style="width:{{(pokemon['pv']/pokemon['pv_max']*100)}}%;"></div>
            </div>
            <p>❤️ {{pokemon['pv']}}/{{pokemon['pv_max']}} HP</p>
        </div>
        <div style="text-align:center;margin:20px 0;">
            <form method="post" style="display:inline-block;margin:10px;">
                <input type="hidden" name="action" value="attack">
                <button class="btn" type="submit">{{T['attack']}}</button>
            </form>
            <form method="post" style="display:inline-block;margin:10px;">
                <input type="hidden" name="action" value="heal">
                <button class="btn" type="submit">{{T['heal']}}</button>
            </form>
        </div>
        <div style="background:#eee;padding:10px;border-radius:10px;margin-top:20px;">
            {% for line in session.get('combat_log', []) %}
            <p>{{line}}</p>
            {% endfor %}
        </div>
        <a href="{{url_for('menu')}}"><button class="btn btn-secondary">{{T['back']}}</button></a>
    </div></body>
    """, T=T, boss=boss, pokemon=pokemon, session=session)

@app.route("/fight_result")
def fight_result():
    if 'username' not in session or 'pokemon_idx' not in session:
        return redirect(url_for("menu"))
    
    lang = session.get("lang", "fr")
    T = LANGUES[lang]
    state = get_state()
    boss = bosses[state['boss_actuel']]
    pokemon = state['collection'][session['pokemon_idx']]
    
    msg = ""
    is_victory = False
    
    if pokemon['pv'] <= 0:
        # Défaite
        state['argent'] += 25
        pokemon['pv'] = max(1, int(pokemon['pv_max'] * 0.25))  # récupère un peu
        msg = T["defeat"]
        is_victory = False
    else:
        # Victoire
        xp_gain = boss["niveau"] * 50
        pokemon["xp"] += xp_gain
        
        # Vérifier montée de niveau
        xp_needed = pokemon["niveau"] * 100
        if pokemon["xp"] >= xp_needed:
            pokemon["niveau"] += 1
            pokemon["xp"] = 0
            pokemon["attaque"] += 3
            pokemon["pv_max"] += 10
            pokemon["pv"] = pokemon["pv_max"]
        
        state['argent'] += boss["recompense"]
        state['boss_actuel'] += 1
        msg = T["victory"]
        is_victory = True
    
    update_state(state)
    
    # Nettoyer la session du combat
    keys_to_clear = ['pokemon_idx', 'boss_pokemon', 'boss_pv', 'boss_pv_max', 'boss_atk', 'combat_log']
    for k in keys_to_clear:
        session.pop(k, None)
    session.modified = True
    
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>{% if is_victory %}🏆 {{T['victory']}}{% else %}💀 {{T['defeat']}}{% endif %}</h1>
        <p style="text-align:center;font-size:1.4em;margin:30px 0;">{{msg}}</p>
        {% if is_victory and state['boss_actuel'] >= bosses|length %}
        <p style="text-align:center;color:#667eea;font-weight:bold;font-size:1.3em;">🎊 Tous les boss sont vaincus !</p>
        {% endif %}
        <a href="{{url_for('menu')}}"><button class="btn">{{T['back']}}</button></a>
    </div></body>
    """, T=T, msg=msg, is_victory=is_victory, state=state, bosses=bosses)

@app.route("/save")
def save():
    if 'username' not in session:
        return redirect(url_for("login_page"))
    save_game(session['username'], get_state())
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>💾 Sauvegarde</h1>
        <p class="msg msg-success">Partie sauvegardée !</p>
        <a href="{{url_for('menu')}}"><button class="btn">Retour au menu</button></a>
    </div></body>
    """)

@app.route("/quit")
def quit():
    session.clear()
    return render_template_string(BASE_STYLE + """
    <body><div class="container">
        <h1>👋 Au revoir !</h1>
        <p style="text-align:center;margin:30px 0;">Merci d'avoir joué !</p>
        <a href="{{url_for('home')}}"><button class="btn">Recommencer</button></a>
    </div></body>
    """)

# ================== RUN SERVER ==================
if __name__ == "__main__":
    app.run(debug=True)
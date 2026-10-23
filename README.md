# Pokémon Game

> **C'est l'un de mes tout premiers jeux !** Je le garde tel quel comme souvenir. La suite, avec plus de corrections, est dans [Pokemon-Game-2.0](https://github.com/Alex12062012/Pokemon-Game-2.0).

Un jeu web inspiré de Pokémon : on ouvre des boosters pour former une équipe, puis on affronte 5 boss de plus en plus forts.

| Menu | Booster | Combat |
|---|---|---|
| ![Menu](docs/menu.jpg) | ![Booster](docs/booster.jpg) | ![Combat](docs/combat.jpg) |

## Le jeu

- **Boosters (50 €)** : un Pokémon au hasard, du Pikachu commun au Mew mythique (2 % de chances).
- **Combats au tour par tour** : *Attaquer* (15 % de coups critiques) ou *Soigner*. Le boss peut aussi se soigner.
- **Progression** : XP et niveaux pour les Pokémon. Une victoire rapporte de l'argent, une défaite +25 €.
- **Reste du jeu** : on peut revendre des Pokémon et soigner l'équipe. Il y a des comptes joueurs, des sauvegardes, et trois langues (FR / EN / RU).

## Lancer le jeu

```bash
pip install -r requirements.txt
python app.py        # ou : sh lancer.sh
```

Ouvre ensuite http://localhost:5000.

## Technique et petite histoire

- **Langage :** Python avec Flask, tout dans un seul fichier `app.py`.
- **Origine du code :** il a été écrit avec l'aide de l'assistant IA Qwen. Les fichiers s'appelaient d'abord `Qwen_python_….py`.
- **Corrections récentes (deux plantages) :**
  - l'écran de victoire faisait une erreur (`'len' is undefined`) ;
  - le combat se trompait de Pokémon (ou plantait) dès qu'un membre de l'équipe était K.O.

---
*Projet de fan, non officiel. Pokémon est une marque de Nintendo / Creatures / Game Freak.*

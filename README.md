# 🌱 Projet Commodities – Stratégie Dynamique de Transition Écologique

Ce projet vise à construire un **indice dynamique d’investissement sur les matières premières** en lien avec la **transition écologique**, en utilisant Python et des données réelles.

---

## 📌 Objectif

Créer une stratégie d’investissement intelligente et évolutive, sous forme d’un **indice dynamique** :
- Investit sur des **mono-indices de matières premières** (cuivre, nickel, pétrole)
- Utilise des **pondérations dynamiques** basées sur des signaux de momentum
- Favorise les matières premières **utiles à la transition énergétique** (cuivre, nickel)
- **Shorte le pétrole** si sa tendance est baissière
- Génère un **indice cumulé simulant une vraie stratégie d’investissement**

---

## ⚙️ Stratégie

- 📈 **Momentum glissant** : variation moyenne sur 20 jours pour détecter les tendances
- 🎯 **Pondérations dynamiques** : plus de poids aux actifs en tendance haussière
- 🔻 **Short pétrole** si momentum < 0
- 🧠 **Protection intégrée** :
  - Poids plafonnés (max 70 %)
  - Rendements mensuels limités entre -20 % et +20 %

---

## 📊 Indicateurs calculés

- **Performance totale**
- **Volatilité annualisée**
- **Sharpe Ratio**
- **Maximum drawdown**
- **Graphiques** :
  - Indice cumulé
  - Évolution des poids alloués

---

## 🧪 Exemple d’exécution

```bash
python main.py

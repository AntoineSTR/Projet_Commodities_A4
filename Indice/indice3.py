import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Charger les données
df = pd.read_csv('data/commodities_prices_final.csv', parse_dates=['Date'])
df = df.sort_values('Date').reset_index(drop=True)
commodities = ['BCOMHG', 'BCOMNI', 'BCOMCL']
df = df.dropna(subset=commodities)

# 2. Calcul du momentum (20 jours)
momentum = df[commodities].pct_change(periods=20)
momentum.columns = [f"{col}_mom" for col in momentum.columns]
df = pd.concat([df, momentum], axis=1)

# 3. Créer une colonne 'Month' pour rebalancing mensuel
df['Month'] = df['Date'].dt.to_period('M')
rebalance_dates = df.drop_duplicates('Month')['Date'].tolist()

# 4. Fonction de pondération dynamique (écologique)
def get_weights(row):
    weights = {}
    total_positive = sum(max(0, row[f"{c}_mom"]) for c in ['BCOMHG', 'BCOMNI'])

    for c in ['BCOMHG', 'BCOMNI']:
        w = max(0, row[f"{c}_mom"])
        weights[c] = w / total_positive if total_positive != 0 else 0

    # Short pétrole si tendance négative
    cl_mom = row['BCOMCL_mom']
    weights['BCOMCL'] = -0.2 if cl_mom < 0 else 0
    return weights

# 5. Initialisation
indice = []
weights_list = []
base_value = {}
df['Indice'] = 0.0

# 6. Boucle principale pour calculer l’indice dynamique
for i, row in df.iterrows():
    t = row['Date']

    if t in rebalance_dates:
        base_value = {c: row[c] for c in commodities}
        current_weights = get_weights(row)
    
    if base_value:
        er = sum(
            current_weights.get(c, 0) * ((row[c] / base_value[c]) - 1)
            for c in commodities
        )
        indice.append(er)
        weights_list.append(current_weights.copy())
    else:
        indice.append(0)
        weights_list.append({c: 0 for c in commodities})

df['Indice'] = indice
df['Indice_Cumule'] = (1 + df['Indice'].fillna(0)).cumprod()

# 7. Créer un DataFrame pour les poids
weights_df = pd.DataFrame(weights_list)
weights_df['Date'] = df['Date']
weights_df = weights_df.set_index('Date')

# 8. Performance & indicateurs
perf = df['Indice_Cumule'].iloc[-1] - 1
vol = df['Indice'].std() * np.sqrt(252)
sharpe = df['Indice'].mean() / df['Indice'].std() * np.sqrt(252)
drawdown = (df['Indice_Cumule'] / df['Indice_Cumule'].cummax()) - 1
max_drawdown = drawdown.min()

# 9. Affichage des résultats
print("📊 STRATÉGIE TRANSITION ÉCOLOGIQUE - RÉSULTATS")
print(f"Performance totale : {perf*100:.2f}%")
print(f"Volatilité annualisée : {vol:.2f}")
print(f"Sharpe Ratio : {sharpe:.2f}")
print(f"Maximum Drawdown : {max_drawdown*100:.2f}%")

# 10. GRAPHIQUE PRINCIPAL : Indice cumulé
plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['Indice_Cumule'], label='Indice Écolo Dynamique (Cumulé)', linewidth=2)
plt.title("Indice Dynamique - Transition Écologique 🌱")
plt.xlabel("Date")
plt.ylabel("Valeur cumulée")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 11. GRAPHIQUE BONUS : Évolution des poids alloués
weights_df.plot.area(figsize=(12,6), title="Évolution des poids alloués aux Commodities")
plt.xlabel("Date")
plt.ylabel("Poids dans la stratégie")
plt.grid(True)
plt.tight_layout()
plt.show()

# 12. (Optionnel) Export du résultat en CSV
# df.to_csv("resultat_indice_eco.csv", index=False)

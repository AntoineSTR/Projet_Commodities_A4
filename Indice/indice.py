import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier CSV avec encodage correct
df = pd.read_csv('data/commodities_prices_final.csv', parse_dates=['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# Colonnes des mono-indices
commodities = ['BCOMHG', 'BCOMNI', 'BCOMCL']

# Poids attribués à chaque indice (modifiable)
weights = {'BCOMHG': 1/3, 'BCOMNI': 1/3, 'BCOMCL': 1/3}

# Générer les dates de rebalancement (mensuelles ici)
df['Month'] = df['Date'].dt.to_period('M')
rebalancing_dates = df.drop_duplicates('Month')['Date'].tolist()

# Initialisation
indice_values = []
base_value = {}
last_rebalance = df['Date'].min()

# Boucle sur chaque ligne pour calculer l'indice
for i, row in df.iterrows():
    t = row['Date']

    # Rebalancement si nouvelle date dans la liste
    if t in rebalancing_dates:
        last_rebalance = t
        base_value = {c: row[c] for c in commodities}

    er = sum(
        weights[c] * ((row[c] / base_value[c]) - 1)
        for c in commodities
    )
    indice_values.append(er)

df['Indice'] = indice_values

# Affichage
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Indice'], label='Indice personnalisé')
plt.title('Évolution de l’indice Commodities')
plt.xlabel('Date')
plt.ylabel('Valeur de l’indice')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

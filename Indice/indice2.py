import pandas as pd
import matplotlib.pyplot as plt

# Charger les données
df = pd.read_csv('data/commodities_prices_final.csv', parse_dates=['Date'])
df = df.sort_values('Date').reset_index(drop=True)

commodities = ['BCOMHG', 'BCOMNI', 'BCOMCL']
df = df.dropna(subset=commodities)

# Calcule du momentum glissant (20 jours)
momentum = df[commodities].pct_change(periods=20)
momentum.columns = [f"{col}_mom" for col in momentum.columns]
df = pd.concat([df, momentum], axis=1)

# Fonction pour attribuer les poids dynamiquement
def get_weights(row):
    weights = {}
    total_positive = sum(max(0, row[f"{c}_mom"]) for c in ['BCOMHG', 'BCOMNI'])
    
    for c in ['BCOMHG', 'BCOMNI']:
        w = max(0, row[f"{c}_mom"])
        weights[c] = w / total_positive if total_positive != 0 else 0

    # Stratégie short sur pétrole si momentum < 0
    cl_mom = row['BCOMCL_mom']
    weights['BCOMCL'] = -0.2 if cl_mom < 0 else 0  # short modéré si momentum négatif
    return weights

# Initialisation
indice = []
base_value = {}
df['Month'] = df['Date'].dt.to_period('M')
rebalance_dates = df.drop_duplicates('Month')['Date'].tolist()
df['Indice'] = 0.0

for i, row in df.iterrows():
    t = row['Date']

    if t in rebalance_dates:
        base_value = {c: row[c] for c in commodities}
        current_weights = get_weights(row)

    er = sum(
        current_weights.get(c, 0) * ((row[c] / base_value[c]) - 1)
        for c in commodities
    )
    indice.append(er)

df['Indice'] = indice

# 🔍 Tracer
plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['Indice'], label='Indice Écolo Dynamique')
plt.title('Indice Dynamique : Stratégie Transition Écologique')
plt.xlabel('Date')
plt.ylabel('Valeur de l’Indice')
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

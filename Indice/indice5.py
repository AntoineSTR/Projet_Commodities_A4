import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === PARAMÈTRES ===
window = 20
rsi_window = 14
commodities = ['BCOMHG', 'BCOMNI', 'BCOMCL']

# === 1. CHARGEMENT DES DONNÉES ===
df = pd.read_csv('data/commodities_prices_final.csv', parse_dates=['Date'])
df = df.sort_values('Date').reset_index(drop=True)
df = df.dropna(subset=commodities)

# === 2. CALCUL DES SIGNAUX ===
for c in commodities:
    df[f"{c}_momentum"] = df[c].pct_change().rolling(window).mean()
    df[f"{c}_mm_signal"] = df[c] - df[c].rolling(window).mean()

    delta = df[c].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    roll_up = pd.Series(gain).rolling(rsi_window).mean()
    roll_down = pd.Series(loss).rolling(rsi_window).mean()
    rs = roll_up / (roll_down + 1e-6)
    df[f"{c}_rsi"] = 100 - (100 / (1 + rs))
    df[f"{c}_rsi_signal"] = (df[f"{c}_rsi"] > 50).astype(int)

# === 3. REBALANCEMENT MENSUEL ===
df['Month'] = df['Date'].dt.to_period('M')
rebalance_dates = df.drop_duplicates('Month')['Date'].tolist()

# === 4. STRATÉGIE DE PONDÉRATION MULTI-SIGNAUX ===
def compute_weights(row):
    weights = {}
    total_score = 0

    for c in ['BCOMHG', 'BCOMNI']:
        score = 0
        if row[f"{c}_momentum"] > 0: score += 1
        if row[f"{c}_mm_signal"] > 0: score += 1
        if row[f"{c}_rsi_signal"] == 1: score += 1
        weights[c] = score
        total_score += score

    for c in ['BCOMHG', 'BCOMNI']:
        weights[c] = min(max(weights[c] / total_score if total_score > 0 else 0, 0), 0.7)

    cl_score = 0
    if row['BCOMCL_momentum'] < 0: cl_score += 1
    if row['BCOMCL_rsi_signal'] == 0: cl_score += 1
    weights['BCOMCL'] = -0.2 if cl_score == 2 else 0

    return weights

# === 5. CALCUL DE L'INDICE ===
indice = []
weights_list = []
base_value = {}
df['Indice'] = 0.0

for i, row in df.iterrows():
    t = row['Date']

    if t in rebalance_dates:
        base_value = {c: row[c] for c in commodities}
        current_weights = compute_weights(row)

    if base_value:
        er = sum(
            current_weights.get(c, 0) * ((row[c] / base_value[c]) - 1)
            for c in commodities
        )
        er = np.clip(er, -0.2, 0.2)
        indice.append(er)
        weights_list.append(current_weights.copy())
    else:
        indice.append(0)
        weights_list.append({c: 0 for c in commodities})

df['Indice'] = indice
df['Indice_Cumule'] = (1 + df['Indice'].fillna(0)).cumprod()

# === 6. ANALYSE DES POIDS ===
weights_df = pd.DataFrame(weights_list)
weights_df['Date'] = df['Date']
weights_df = weights_df.set_index('Date')

# === 7. INDICATEURS DE PERFORMANCE ===
perf = df['Indice_Cumule'].iloc[-1] - 1
vol = df['Indice'].std() * np.sqrt(252)
sharpe = df['Indice'].mean() / df['Indice'].std() * np.sqrt(252)
drawdown = (df['Indice_Cumule'] / df['Indice_Cumule'].cummax()) - 1
max_drawdown = drawdown.min()

print("📊 STRATÉGIE DYNAMIQUE ÉCOLOGIQUE - V3")
print(f"Performance totale : {perf*100:.2f}%")
print(f"Volatilité annualisée : {vol:.2f}")
print(f"Sharpe Ratio : {sharpe:.2f}")
print(f"Max Drawdown : {max_drawdown*100:.2f}%")

# === 8. GRAPHIQUES ===

# Indice cumulé
plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['Indice_Cumule'], label='Indice cumulé', linewidth=2)
plt.title("Indice Dynamique Écologique V3 🌿")
plt.xlabel("Date")
plt.ylabel("Valeur cumulée")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Poids alloués
weights_df.plot.area(figsize=(12,6), title="Évolution des poids dans la stratégie (V3)")
plt.xlabel("Date")
plt.ylabel("Poids")
plt.grid(True)
plt.tight_layout()
plt.show()

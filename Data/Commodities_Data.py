import pandas as pd

# === 1. Charger les données ===
copper = pd.read_csv("data/Copper Futures Historical Data.csv")
nickel = pd.read_csv("data/Futures nickel - Données Historiques.csv")
oil = pd.read_csv("data/Crude Oil WTI Futures Historical Data.csv")

# === 2. Conversion des dates ===
copper["Date"] = pd.to_datetime(copper["Date"], format="%m/%d/%Y")
nickel["Date"] = pd.to_datetime(nickel["Date"], format="%d/%m/%Y")
oil["Date"] = pd.to_datetime(oil["Date"], format="%m/%d/%Y")

# === 3. Nettoyage et renommage ===
copper = copper[["Date", "Price"]].rename(columns={"Price": "BCOMHG"})
nickel = nickel[["Date", "Dernier"]].rename(columns={"Dernier": "BCOMNI"})
oil = oil[["Date", "Price"]].rename(columns={"Price": "BCOMCL"})

# Nickel : convertir "14.452,63" → 14452.63
nickel["BCOMNI"] = (
    nickel["BCOMNI"]
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# === 4. Merge strict sur la date (inner join) ===
df = copper.merge(nickel, on="Date").merge(oil, on="Date")
df = df.sort_values("Date").set_index("Date")

# === 5. Sauvegarde CSV ===
df.to_csv("data/commodities_prices_final.csv")
print("✅ Fichier commodities_prices_final.csv créé avec succès.")

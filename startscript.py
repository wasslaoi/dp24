# begin met:
# pip install sqlalchemy
# pip install pymysql
# pip install cryptography   

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# Databaseconfiguratie
host = "localhost"
port = 3306  # Standaard MariaDB/MySQL-poort, kan ook 3307 zijn
database = "hr"
user = "kpimaintenance"
password = "Kpi2025!"
view_name = "view_kpi_bezettingsgraad_machinist"  # de view voor jouw kpi-story


# Maak een databaseverbinding met SQLAlchemy en pymysql
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# Inlezen van databaseview
try:
    df = pd.read_sql(f"SELECT * FROM {view_name}", con=engine)
    print("Eerste regels van de KPI-view:")
    print(df.head())
except Exception as e:
    print("Fout bij ophalen van data:", e)

# locatie json-bestand en logboek
bestandspad = "shuttle_log.json"      # shuttle logfile
excelfile = "trein_logboek.xlsx"      # trein logboek (oude situatie)


# Inlezen van het JSON-bestand in een DataFrame
df2 = pd.read_json(bestandspad)
print("\nEerste regels van shuttle_log.json:")
print(df2.head())


# Inlezen van het Excel-bestand (trein log)
try:
    df_excel = pd.read_excel(excelfile, sheet_name="Logboek")
    print("\nTrein Excel-log ingelezen (blad Logboek):")
    print(df_excel.head())
except Exception as e:
    print("Fout bij het inlezen van de Excel:", e)


# datums omzetten naar datetime
df2["datum"] = pd.to_datetime(df2["datum"], dayfirst=True)
df_excel["datum"] = pd.to_datetime(df_excel["datum"], dayfirst=True)


# Filter periode shuttle: 21-11-2025 t/m 27-11-2025
start_shuttle = "2025-11-21"
eind_shuttle  = "2025-11-27"

mask_shuttle = (df2["datum"] >= start_shuttle) & (df2["datum"] <= eind_shuttle)
df_shuttle_week = df2[mask_shuttle]

print("\nShuttle-ritten in geselecteerde periode:")
print(df_shuttle_week[["datum", "rit_nummer", "aantal_passagiers"]].head())
print("Aantal ritten shuttle na filter:", len(df_shuttle_week))

# Bereken bezettingsgraad shuttle berekening (KPI)
df_shuttle_week["bezettingsgraad_pct"] = (df_shuttle_week["aantal_passagiers"] / 50) * 100

print("\nEerste bezettingsgraden voor SHUTTLE:")
print(df_shuttle_week[["datum", "rit_nummer", "aantal_passagiers", "bezettingsgraad_pct"]].head())

# Gemiddelde bezettingsgraad shuttle (voor KPI-tegel)
gem_bezet_shuttle = df_shuttle_week["bezettingsgraad_pct"].mean()
print("\nGemiddelde bezettingsgraad SHUTTLE:", round(gem_bezet_shuttle, 1), "%")


# Filter periode trein: 11-08-2025 t/m 17-08-2025
start_trein = "2025-08-11"
eind_trein  = "2025-08-17"

mask_trein = (df_excel["datum"] >= start_trein) & (df_excel["datum"] <= eind_trein)
df_trein_week = df_excel[mask_trein]

print("\nTrein-ritten in geselecteerde periode:")
print(df_trein_week[["datum", "rit_nummer", "aantal_passagiers"]].head())
print("Aantal ritten trein na filter:", len(df_trein_week))

# Bereken bezettingsgraad trein (KPI)
df_trein_week["bezettingsgraad_pct"] = (df_trein_week["aantal_passagiers"] / 50) * 100

print("\nEerste bezettingsgraden voor tre:")
print(df_trein_week[["datum", "rit_nummer", "aantal_passagiers", "bezettingsgraad_pct"]].head())

# Gemiddelde bezettingsgraad trein (voor KPI-tegel)
gem_bezet_trein = df_trein_week["bezettingsgraad_pct"].mean()
print("\nGemiddelde bezettingsgraad TREIN:", round(gem_bezet_trein, 1), "%")

# DataFrame maken voor de vergelijking (hoofdscherm)
samenvatting = pd.DataFrame({
    "vervoersmiddel": ["Trein (oude situatie)", "Shuttle (pilot)"],
    "gem_bezettingsgraad_pct": [gem_bezet_trein, gem_bezet_shuttle]
})

print("\nSAMENVATTING GEMIDDELDE BEZETTINGSGRAAD:")
print(samenvatting)

# Barplot maken voor hoofdscherm (KPI-visualisatie)
sns.set_theme(style="whitegrid")
sns.set_palette("deep")
plt.figure(figsize=(8, 5), dpi=120)

sns.barplot(x="vervoersmiddel",
            y="gem_bezettingsgraad_pct",
            data=samenvatting)

plt.ylabel("Gemiddelde bezettingsgraad (%)")
plt.xlabel("Vervoersmiddel")
plt.title("Gemiddelde bezettingsgraad Trein (oud) vs Shuttle (pilot)")

# Waarden boven de balken
for i, v in enumerate(samenvatting["gem_bezettingsgraad_pct"]):
    plt.text(i, v + 1, f"{v:.1f}%", ha='center', fontweight='bold')

plt.tight_layout()
plt.show()


# KPI-tegel met de twee gemiddelde bezettingsgraden
plt.figure(figsize=(7, 3), dpi=120)
plt.axis("off")

plt.title("KPI Gemiddelde Bezettingsgraad", pad=15, fontsize=12, fontweight="bold")

plt.text(0.1, 0.55, "Trein (oud)", fontsize=10)
plt.text(0.1, 0.25, f"{round(gem_bezet_trein, 1)}%", fontsize=22, fontweight="bold")

plt.text(0.55, 0.55, "Shuttle (pilot)", fontsize=10)
plt.text(0.55, 0.25, f"{round(gem_bezet_shuttle, 1)}%", fontsize=22, fontweight="bold")

plt.show()

# Lijngrafiek per dagnummer (1 t/m 7) trein vs shuttle

# Gemiddelde bezettingsgraad per dag berekenen
trein_per_datum = (
    df_trein_week
    .groupby("datum")["bezettingsgraad_pct"]
    .mean()
    .reset_index()
    .sort_values("datum")
    .reset_index(drop=True)
)

shuttle_per_datum = (
    df_shuttle_week
    .groupby("datum")["bezettingsgraad_pct"]
    .mean()
    .reset_index()
    .sort_values("datum")
    .reset_index(drop=True)
)

# 2. Dagnummer toevoegen (1 t/m 7)
trein_per_datum["dag"] = trein_per_datum.index + 1
trein_per_datum["vervoersmiddel"] = "Trein"

shuttle_per_datum["dag"] = shuttle_per_datum.index + 1
shuttle_per_datum["vervoersmiddel"] = "Shuttle"

# 3. Samenvoegen voor Seaborn
bezetting_per_dagnummer = pd.concat(
    [trein_per_datum[["dag", "vervoersmiddel", "bezettingsgraad_pct"]],
     shuttle_per_datum[["dag", "vervoersmiddel", "bezettingsgraad_pct"]]],
    ignore_index=True
)

# 4. Lijngrafiek maken 
sns.set_theme(style="whitegrid")

plt.figure(figsize=(8, 5), dpi=120)

sns.lineplot(
    data=bezetting_per_dagnummer,
    x="dag",
    y="bezettingsgraad_pct",
    hue="vervoersmiddel",
    marker="o"
)

plt.title("Bezettingsgraad per dag (1 t/m 7)  Trein (oud) vs Shuttle (pilot)")
plt.xlabel("Dag van de week")
plt.ylabel("Gemiddelde bezettingsgraad (%)")
plt.xticks([1, 2, 3, 4, 5, 6, 7])
plt.legend(title="Vervoersmiddel")
plt.tight_layout()
plt.xlim(1, 7)
plt.show()







# modele_utils.py — code partagé par 04_modeles et 05_evaluation_finale
#
# Tous les réglages viennent de config.py (graine, chemins, variables, euros).

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

import config

RACINE = Path(__file__).resolve().parent
CLASSE_A_DETECTER = "neutral or dissatisfied"

CATEGORIELLES = ["Customer Type", "Type of Travel", "Class"]
NUMERIQUES = [v for v in config.FEATURES_MODELE if v not in CATEGORIELLES]

# Gain net d'une approche (voir config) : +60 € sur un insatisfait, -40 € sinon
GAIN_BON_CHOIX = config.GAIN_VRAI_INSATISFAIT - config.COUT_APPROCHE
GAIN_MAUVAIS_CHOIX = -config.COUT_APPROCHE


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
def _chemin(relatif):
    chemin = RACINE / relatif
    if not chemin.exists():
        # Les CSV sont actuellement poussés dans data/raw/
        chemin = RACINE / "data" / "raw" / Path(relatif).name
    return chemin


def _charger(relatif):
    df = pd.read_csv(_chemin(relatif))
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")] + ["id"])
    # Quelques retards à l'arrivée manquants : on reprend le retard au départ,
    # très proche et lui aussi connu à l'atterrissage.
    df["Arrival Delay in Minutes"] = df["Arrival Delay in Minutes"].fillna(
        df["Departure Delay in Minutes"]
    )
    y = (df[config.TARGET] == CLASSE_A_DETECTER).astype(int).to_numpy()
    return df, y


def charger_train():
    return _charger(config.TRAIN_PATH)


def charger_test():
    """À n'appeler qu'une seule fois, dans 05_evaluation_finale."""
    return _charger(config.TEST_PATH)


# ---------------------------------------------------------------------------
# Règles simples (sans modèle)
# ---------------------------------------------------------------------------
# Un score plus élevé = passager à aborder en priorité.
# Les ex aequo sont départagés au hasard (on prend le résultat moyen).
REGLES = {
    "Voyage personnel": lambda df: (df["Type of Travel"] == "Personal Travel").astype(float),
    "Classe Eco / Eco Plus": lambda df: (df["Class"] != "Business").astype(float),
    "Client non fidèle": lambda df: (df["Customer Type"] == "disloyal Customer").astype(float),
    "Plus gros retard à l'arrivée": lambda df: df["Arrival Delay in Minutes"].astype(float),
}


# ---------------------------------------------------------------------------
# Modèles
# ---------------------------------------------------------------------------
def regression_logistique():
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(drop="first"), CATEGORIELLES),
        # Retards et distance très étalés : on les compresse avec un log
        ("num", Pipeline([("log", FunctionTransformer(np.log1p)), ("std", StandardScaler())]), NUMERIQUES),
    ])
    return Pipeline([("prep", prep), ("clf", LogisticRegression(max_iter=1000))])


def arbre_decision(categorielles=CATEGORIELLES, numeriques=NUMERIQUES):
    """Arbre retenu. Les arguments ne servent qu'aux variantes de contrôle
    (avec l'âge, sans le motif du voyage)."""
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(), categorielles),
        ("num", "passthrough", numeriques),
    ], verbose_feature_names_out=False)
    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=config.SEED)
    return Pipeline([("prep", prep), ("clf", clf)])


MODELES = {
    "Régression logistique": regression_logistique,
    "Arbre de décision": arbre_decision,
}

# Choix fait dans 04_modeles, à partir du train uniquement
MODELE_RETENU = "Arbre de décision"
REGLE_DE_REFERENCE = "Voyage personnel"


# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------
def selection_top(score, capacite=config.CAPACITE):
    """Part de chaque passager dans les `capacite` % les plus à risque.
    Les ex aequo à la limite se partagent les places restantes."""
    score = np.asarray(score, dtype=float)
    k = capacite * len(score)
    seuil = np.sort(score)[::-1][int(np.ceil(k)) - 1]
    au_dessus = score > seuil
    egaux = score == seuil
    poids = au_dessus.astype(float)
    poids[egaux] = (k - au_dessus.sum()) / egaux.sum()
    return poids


def evaluer(y, score, capacite=config.CAPACITE):
    poids = selection_top(score, capacite)
    abordes = poids.sum()
    bons = (poids * y).sum()
    precision = bons / abordes
    # Formule du groupe : passagers abordés × (précision × 100 € − 40 €)
    gain = abordes * (precision * config.GAIN_VRAI_INSATISFAIT - config.COUT_APPROCHE)
    return {
        "AUC": roc_auc_score(y, score),
        "Précision top 10 %": precision,
        "Gain / 1000 passagers (€)": gain / len(y) * 1000,
        "Passagers abordés": abordes,
        "Bons choix": bons,
        "Mauvais choix": abordes - bons,
        "Gain total (€)": gain,
    }


def gain_parfait_par_1000(y, capacite=config.CAPACITE):
    return min(capacite, y.mean()) * 1000 * GAIN_BON_CHOIX


# ---------------------------------------------------------------------------
# Validation croisée (train uniquement)
# ---------------------------------------------------------------------------
def plis(y, n_plis=5):
    cv = StratifiedKFold(n_plis, shuffle=True, random_state=config.SEED)
    return list(cv.split(np.zeros(len(y)), y))


def scores_hors_pli(df, y, fabrique, decoupage, colonnes=config.FEATURES_MODELE):
    """Chaque passager est noté par un modèle qui ne l'a pas vu à l'entraînement."""
    X = df[colonnes]
    score = np.zeros(len(y))
    for app, val in decoupage:
        modele = fabrique().fit(X.iloc[app], y[app])
        score[val] = modele.predict_proba(X.iloc[val])[:, 1]
    return score


def cv(y, score, decoupage):
    """Résultats pli par pli à partir des scores hors pli."""
    return pd.DataFrame([evaluer(y[val], score[val]) for _, val in decoupage])

# modele_utils.py — code partagé par 04_modeles et 05_evaluation_finale
#
# Tous les réglages viennent de config.py (graine, chemins, variables, euros).

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
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
    assert df[config.FEATURES_MODELE].notna().all().all(), "Valeurs manquantes dans les variables du modèle"
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

# Résumé de l'arbre en 3 questions, pour l'expliquer à la direction.
# Le groupe visé couvre environ 9,8 % des passagers.
NOM_REGLE_3_QUESTIONS = "Règle 3 questions (hors Business, voyage perso, retard > 5 min)"


def regle_3_questions(df):
    return ((df["Class"] != "Business")
            & (df["Type of Travel"] == "Personal Travel")
            & (df["Arrival Delay in Minutes"] > 5)).astype(float)


# ---------------------------------------------------------------------------
# Modèles
# ---------------------------------------------------------------------------
def regression_logistique():
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), CATEGORIELLES),
        # Retards et distance très étalés : on les compresse avec un log
        ("num", Pipeline([("log", FunctionTransformer(np.log1p)), ("std", StandardScaler())]), NUMERIQUES),
    ])
    return Pipeline([("prep", prep), ("clf", LogisticRegression(max_iter=1000))])


def arbre_decision(categorielles=CATEGORIELLES, numeriques=NUMERIQUES):
    """Arbre retenu. Les arguments ne servent qu'aux variantes de contrôle
    (avec l'âge, sans le motif du voyage)."""
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorielles),
        ("num", "passthrough", numeriques),
    ], verbose_feature_names_out=False)
    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=config.SEED)
    return Pipeline([("prep", prep), ("clf", clf)])


def gradient_boosting():
    """Modèle « boîte noire » de comparaison : vérifie qu'on ne perd rien
    à choisir un modèle explicable."""
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORIELLES),
        ("num", "passthrough", NUMERIQUES),
    ], verbose_feature_names_out=False)
    clf = HistGradientBoostingClassifier(random_state=config.SEED)
    return Pipeline([("prep", prep), ("clf", clf)])


MODELES = {
    "Régression logistique": regression_logistique,
    "Arbre de décision": arbre_decision,
    "Gradient boosting": gradient_boosting,
}

# Choix fait dans 04_modeles, à partir du train uniquement
MODELE_RETENU = "Arbre de décision"
REGLE_DE_REFERENCE = "Voyage personnel"


# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------
def selection_top(score, capacite=config.CAPACITE, ex_aequo="tirage"):
    """Part de chaque passager dans les `capacite` % les plus à risque.

    L'arbre donne le même score à tout un groupe : la limite des 10 % tombe
    souvent au milieu d'une case.
    - ex_aequo="tirage"  : on complète par tirage au sort dans cette case
      (résultat moyen du tirage) ;
    - ex_aequo="exclure" : on s'arrête à la dernière case entière.
    """
    score = np.asarray(score, dtype=float)
    k = capacite * len(score)
    seuil = np.sort(score)[::-1][int(np.ceil(k)) - 1]
    au_dessus = score > seuil
    egaux = score == seuil
    poids = au_dessus.astype(float)
    if ex_aequo == "tirage":
        poids[egaux] = (k - au_dessus.sum()) / egaux.sum()
    return poids


def evaluer(y, score, capacite=config.CAPACITE, ex_aequo="tirage"):
    poids = selection_top(score, capacite, ex_aequo)
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
# Dessin de l'arbre (en français, pour le rapport et les slides)
# ---------------------------------------------------------------------------
QUESTIONS_OUI_NON = {
    "Class_Business": "Classe Business ?",
    "Class_Eco": "Classe Eco ?",
    "Class_Eco Plus": "Classe Eco Plus ?",
    "Type of Travel_Business travel": "Voyage professionnel ?",
    "Type of Travel_Personal Travel": "Voyage personnel ?",
    "Customer Type_Loyal Customer": "Client fidèle ?",
    "Customer Type_disloyal Customer": "Client non fidèle ?",
}
QUESTIONS_SEUIL = {
    "Flight Distance": ("Distance du vol\nsupérieure à", ""),  # unité non précisée par le sujet
    "Departure Delay in Minutes": ("Retard au départ\nde plus de", "min"),
    "Arrival Delay in Minutes": ("Retard à l'arrivée\nde plus de", "min"),
    "Age": ("Plus de", "ans"),
}


def _question(variable, seuil):
    if variable in QUESTIONS_OUI_NON:
        return QUESTIONS_OUI_NON[variable]
    debut, unite = QUESTIONS_SEUIL[variable]
    return f"{debut} {int(np.floor(seuil))}{' ' + unite if unite else ''} ?"


def dessiner_arbre(pipeline, chemin=None, capacite=config.CAPACITE):
    """Arbre lu de gauche à droite : « Oui » vers le haut, « Non » vers le bas.
    La couleur des cases finales indique la part de passagers mécontents."""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import FancyBboxPatch

    arbre = pipeline.named_steps["clf"].tree_
    noms = pipeline.named_steps["prep"].get_feature_names_out()
    total = arbre.n_node_samples[0]
    part = arbre.n_node_samples / total
    taux = arbre.value[:, 0, 1] / arbre.value[:, 0, :].sum(axis=1)
    feuille = arbre.children_left == -1

    # Cases visées quand on aborde les `capacite` passagers les plus à risque.
    # La dernière case n'est souvent prise qu'en partie (tirage au sort).
    prioritaires, en_partie, cumul = set(), {}, 0.0
    for n in sorted(np.flatnonzero(feuille), key=lambda n: -taux[n]):
        if cumul >= capacite:
            break
        if cumul + part[n] > capacite:
            en_partie[n] = (capacite - cumul) / part[n]
        prioritaires.add(n)
        cumul += part[n]

    # Placement : profondeur en x, feuilles empilées en y (« Oui » au-dessus)
    pos, profondeur_max = {}, 0
    rang = iter(range(feuille.sum()))

    def placer(n, prof):
        nonlocal profondeur_max
        profondeur_max = max(profondeur_max, prof)
        if feuille[n]:
            pos[n] = (prof, -next(rang))
        else:
            oui, non = arbre.children_right[n], arbre.children_left[n]
            placer(oui, prof + 1)
            placer(non, prof + 1)
            pos[n] = (prof, (pos[oui][1] + pos[non][1]) / 2)

    placer(0, 0)

    ENCRE, ENCRE_2, TRAIT, FOND = "#0b0b0b", "#52514e", "#c3c2b7", "#fcfcfb"
    bleus = LinearSegmentedColormap.from_list(
        "bleus", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    COL, LARG, HAUT = 4.1, 2.9, 0.78   # écart entre colonnes, taille des cases

    n_feuilles = feuille.sum()
    fig, ax = plt.subplots(figsize=(17, 0.72 * n_feuilles + 2.6))
    fig.patch.set_facecolor(FOND)
    ax.set_facecolor(FOND)

    def x_case(n):
        return pos[n][0] * COL

    # Liens coudés + étiquettes Oui / Non
    for n in pos:
        if feuille[n]:
            continue
        x0, y0 = x_case(n) + LARG / 2, pos[n][1]
        for enfant, mot in [(arbre.children_right[n], "Oui"), (arbre.children_left[n], "Non")]:
            x1, y1 = x_case(enfant) - LARG / 2, pos[enfant][1]
            xm = (x0 + x1) / 2
            ax.plot([x0, xm, xm, x1], [y0, y0, y1, y1], color=TRAIT, lw=1.6, zorder=1,
                    solid_joinstyle="round")
            ax.text(xm + 0.08, y1 + 0.12, mot, fontsize=9.5, color=ENCRE_2,
                    fontweight="bold", va="bottom", ha="left")

    # Cases
    for n, (prof, y) in pos.items():
        x = x_case(n)
        if feuille[n]:
            couleur = bleus(taux[n])
            r, g, b, _ = couleur
            texte = "white" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.45 else ENCRE
            prio = n in prioritaires
            ax.add_patch(FancyBboxPatch(
                (x - LARG / 2, y - HAUT / 2), LARG, HAUT, boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=couleur, edgecolor=ENCRE if prio else "none", lw=2.2 if prio else 0, zorder=2))
            ax.text(x, y + 0.12, f"{taux[n]:.0%} mécontents".replace("%", " %"),
                    ha="center", va="center", fontsize=11, fontweight="bold", color=texte, zorder=3)
            ax.text(x, y - 0.18, f"{part[n]:.1%} des passagers".replace(".", ",").replace("%", " %"),
                    ha="center", va="center", fontsize=9, color=texte, zorder=3)
            if prio:
                etiquette = ("◀ À aborder\n    en priorité" if n not in en_partie else
                             f"◀ En partie : {en_partie[n]:.0%}\n    tirés au sort".replace("%", " %"))
                ax.text(x + LARG / 2 + 0.15, y, etiquette, ha="left", va="center",
                        fontsize=9, fontweight="bold", color=ENCRE, zorder=3)
        else:
            ax.add_patch(FancyBboxPatch(
                (x - LARG / 2, y - HAUT / 2), LARG, HAUT, boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor="white", edgecolor=TRAIT, lw=1.2, zorder=2))
            question = _question(noms[arbre.feature[n]], arbre.threshold[n])
            haut = 0.1 if "\n" not in question else 0.14
            ax.text(x, y + haut, question, ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=ENCRE, zorder=3, linespacing=1.1)
            ax.text(x, y - 0.27, f"{part[n]:.0%} des passagers · {taux[n]:.0%} mécontents".replace("%", " %"),
                    ha="center", va="center", fontsize=8, color=ENCRE_2, zorder=3)

    ax.set_xlim(-LARG / 2 - 0.2, profondeur_max * COL + LARG / 2 + 1.6)
    ax.set_ylim(-(n_feuilles - 1) - 0.7, 0.7)
    ax.axis("off")

    fig.suptitle("Comment l'arbre de décision repère les passagers à aborder", x=0.02, ha="left",
                 fontsize=16, fontweight="bold", color=ENCRE)
    fig.text(0.02, 0.945,
             "On suit les questions de gauche à droite : « Oui » monte, « Non » descend. "
             "Chaque case finale donne la part de passagers mécontents dans ce groupe.",
             fontsize=10.5, color=ENCRE_2)

    # Légende des couleurs
    cax = fig.add_axes([0.62, 0.035, 0.3, 0.018])
    barre = fig.colorbar(plt.cm.ScalarMappable(cmap=bleus, norm=plt.Normalize(0, 100)),
                         cax=cax, orientation="horizontal")
    barre.set_label("Part de passagers mécontents dans la case (%)", fontsize=9.5, color=ENCRE_2)
    barre.outline.set_visible(False)
    barre.ax.tick_params(labelsize=9, colors=ENCRE_2, length=0)
    fig.text(0.02, 0.04, f"Encadré noir : cases visées quand les équipes abordent les {capacite:.0%} "
             "passagers les plus à risque "
             "(la dernière case n'est prise qu'en partie, par tirage au sort).".replace("%", " %"),
             fontsize=9.5, color=ENCRE_2)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.91, bottom=0.09)
    if chemin:
        fig.savefig(chemin, dpi=170, facecolor=FOND)
    return fig


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


def cv(y, score, decoupage, capacite=config.CAPACITE, ex_aequo="tirage"):
    """Résultats pli par pli à partir des scores hors pli.
    Les chiffres annoncés sont toujours la moyenne de ces 5 plis."""
    return pd.DataFrame([evaluer(y[val], score[val], capacite, ex_aequo) for _, val in decoupage])

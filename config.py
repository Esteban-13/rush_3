# config.py — réglages partagés par tout le groupe
 
SEED = 42  # graine aléatoire : garantit les mêmes résultats à chaque exécution
 
TRAIN_PATH = "data/raw/train.csv"
TEST_PATH = "data/raw/test.csv"  # ne s'ouvre QUE dans 05_evaluation_finale
 
TARGET = "satisfaction"
 
# Variables connues à l'atterrissage (utilisées par le modèle)
FEATURES_MODELE = [
    "Customer Type", "Type of Travel", "Class",
    "Flight Distance", "Departure Delay in Minutes", "Arrival Delay in Minutes",
]
 
# Hypothèses économiques de la directrice
COUT_APPROCHE = 40
GAIN_VRAI_INSATISFAIT = 100   # 1/3 × 1/2 × 600 €
CAPACITE = 0.10               # 10 % des passagers max
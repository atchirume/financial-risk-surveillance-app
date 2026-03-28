from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR / "data" / "raw"
MODELS_DIR = APP_DIR / "models"
OUTPUTS_DIR = APP_DIR / "outputs"

RANDOM_SEED = 42
DEFAULT_ALERT_RATE = 0.01

W_SUPERVISED = 0.52
W_RULES = 0.18
W_ANOMALY = 0.12
W_GRAPH = 0.10
W_TBML = 0.08
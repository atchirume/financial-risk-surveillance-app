from pathlib import Path

# Update this if your AML data is stored elsewhere
BASE_DIR = Path("/Users/USER/Documents/Models and Programs/Anti Money Laundering Risk management framework/aml_ml_system")
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

RANDOM_SEED = 42
DEFAULT_ALERT_RATE = 0.01  # top 1%

# Fused score weights
W_SUPERVISED = 0.52
W_RULES = 0.18
W_ANOMALY = 0.12
W_GRAPH = 0.10
W_TBML = 0.08

"""Central configuration for the CAISO KAN forecasting replication."""

# ── Data ──────────────────────────────────────────────────────────────────────
START_YEAR = 2015
END_YEAR   = 2024

# API keys – fill these in before running scripts/fetch_data.py
NOAA_TOKEN = "YOUR_NOAA_CDO_TOKEN"   # free at https://www.ncdc.noaa.gov/cdo-web/token
EIA_API_KEY = "YOUR_EIA_API_KEY"     # free at https://www.eia.gov/opendata/register.php
# BLS public API works without a key (rate-limited); set if you have one
BLS_API_KEY = ""

# California FIPS code for NOAA
NOAA_LOCATION_ID = "FIPS:06"
# BLS West urban CPI series (analogous to UK CPI)
BLS_SERIES_ID = "CUURA422SA0"

# ── Preprocessing ─────────────────────────────────────────────────────────────
WINDOW_SIZE  = 20    # look-back months (paper: 20)
TRAIN_RATIO  = 0.80  # 80 / 20 split
RANDOM_SEED  = 42

# ── Model hyperparameters ─────────────────────────────────────────────────────
INPUT_SIZE   = 9     # number of features (target + 8 exogenous)
HIDDEN_SIZE  = 64
OUTPUT_SIZE  = 1

# KAN layer (paper: grid_size=200, spline_order=3, noise_scale=0.1, grid_eps=0.02)
KAN_GRID_SIZE   = 200   # reduce to 5-20 for faster experiments
KAN_SPLINE_ORDER = 3
KAN_NOISE_SCALE = 0.1
KAN_GRID_EPS    = 0.02  # weight between adaptive and uniform grid

# TCN
TCN_NUM_CHANNELS = [64, 64]
TCN_KERNEL_SIZE  = 3
TCN_DROPOUT      = 0.2

# Transformer
TRANSFORMER_D_MODEL     = 64
TRANSFORMER_NHEAD       = 4
TRANSFORMER_NUM_LAYERS  = 2
TRANSFORMER_DIM_FF      = 256
TRANSFORMER_DROPOUT     = 0.1

# ── Training ──────────────────────────────────────────────────────────────────
BATCH_SIZE    = 32
MAX_EPOCHS    = 200
LEARNING_RATE = 1e-3
PATIENCE      = 20   # early stopping patience

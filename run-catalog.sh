source .venv/bin/activate
pip install -r requirements.txt
export  GOOGLE_APPLICATION_CREDENTIALS="secrets/credentials.json"
clear
python3 catalog_update.py neon-camera-403606 us-central1 neon-camera-catalog-labelled
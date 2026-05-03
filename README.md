# SmartEmotionTracker-advanced
Ready-to-run advanced emotion tracker using Streamlit, DeepFace, and MediaPipe.

## What's inside
- Live webcam emotion detection (DeepFace)
- Eye/blink detection (MediaPipe FaceMesh)
- Streamlit web dashboard (app.py)
- CSV logging (logs/emotion_log.csv)
- ESP32 HTTP alert helper (esp32_alert.py)

## Quick start (Windows)
1. Open PowerShell and navigate to the project folder:
   ```
   cd path\to\SmartEmotionTracker-advanced
   ```
2. Create and activate virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   python -m pip install --upgrade pip
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > Note: `tensorflow` and DeepFace models may download on first run and can be large.
4. Run Streamlit app:
   ```
   streamlit run app.py
   ```
5. Open the URL shown in terminal (usually http://localhost:8501).

## ESP32
- Update `ESP32_IP` in `esp32_alert.py` with your device IP.
- ESP32 should run a simple webserver that responds to `/alert?msg=...`.

## Troubleshooting
- If camera not accessible, change camera index in Streamlit sidebar.
- If DeepFace fails to load models, ensure internet on first run and check tensorflow installation.

## Files
- app.py: Streamlit dashboard (main)
- camera_stream.py: MediaPipe + webcam wrapper
- emotion_model.py: DeepFace wrapper
- logger.py: CSV logger
- esp32_alert.py: ESP32 HTTP alert
- assets/happy.mp3: example sound (empty placeholder)

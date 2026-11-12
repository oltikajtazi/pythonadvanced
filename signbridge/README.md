# Signbridge

Webcam sign recognition plus speech to signs. MediaPipe tracks your hand in the browser, Python recognises the sign, SQLite stores everything.

## Run

```
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:8000 in Chrome or Edge and allow the camera. Internet is needed for the MediaPipe files and fonts.

## Use

1. **Teach a sign:** type a word, press Record, hold the sign and tilt your hand slightly. Do 2–3 rounds per sign, for at least 2 signs.
2. **Train model:** five models compete (neural network, random forest, k-nearest neighbours, SVM, and a voting ensemble of the best) and the best one is kept.
3. **Sign:** hold a sign for about a second and the word is added to your sentence. Press Speak to hear it.
4. **Voice to signs:** press Listen (or type) and each known word is shown as a hand drawing.

## Start with a ready-made alphabet (optional)

Instead of recording every sign yourself, import a hand-landmark CSV (for example an ASL alphabet dataset with a label column and 63 x,y,z columns):

```
(stop the server with Ctrl+C first)
python import_dataset.py path\to\landmarks.csv
python server.py
```

It keeps up to 300 samples per sign, stores a mirrored copy of each so either hand works, then trains all candidate models. Run it once per dataset. Your own recorded signs are added to the same database, so you can mix both.

## Files

- `import_dataset.py`: loads a landmark CSV into the database and trains on it
- `server.py`: FastAPI REST endpoints and the WebSocket used for live recognition
- `model.py`: landmark normalisation, training and prediction
- `database.py`: SQLite tables `samples`, `models`, `translations` (file: `data/signbridge.db`)
- `static/`: the web interface (`index.html`, `style.css`, `app.js`)

## Notes

- Accuracy is measured with cross-validation on your own recordings. Samples from one round are very similar, so the number is optimistic until you record several rounds.
- This recognises static hand poses (letters, numbers, simple words). Moving signs need a sequence model (LSTM) over many frames, which is the natural next step.

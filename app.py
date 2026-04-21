from flask import Flask, request, render_template_string, redirect, url_for
import csv
import os
import requests
from datetime import datetime

app = Flask(__name__)

# ─── Data ────────────────────────────────────────────────────────────────────
# Позже можно заменить на загрузку из CSV/Excel файла
DOCTORS = {
    "1647495": "https://disk.360.yandex.ru/i/LmYtUYgu58mIyg",
    "2034578": "https://disk.360.yandex.ru/i/zlLYlmVwF26qMQ",
    "2982837": "https://disk.360.yandex.ru/i/WR_iFdQQwquWAA",
}

RESPONSES_FILE = "responses.csv"

STATUS_LABELS = {
    "approve": "✅ Нравится",
    "edit":    "✏️ Нужны правки",
    "decline": "❌ Отказываюсь от размещения",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_direct_image_url(public_url: str) -> str:
    """Получает прямую ссылку на изображение через Яндекс Диск API."""
    try:
        r = requests.get(
            "https://cloud-api.yandex.net/v1/disk/public/resources/download",
            params={"public_key": public_url},
            timeout=5,
        )
        r.raise_for_status()
        return r.json().get("href", public_url)
    except Exception:
        return public_url  # fallback на оригинальную ссылку


def save_response(doctor_id: str, status: str):
    file_exists = os.path.exists(RESPONSES_FILE)
    with open(RESPONSES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["doctor_id", "status", "label", "timestamp"])
        writer.writerow([
            doctor_id,
            status,
            STATUS_LABELS.get(status, status),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ])


def already_responded(doctor_id: str) -> bool:
    if not os.path.exists(RESPONSES_FILE):
        return False
    with open(RESPONSES_FILE, newline="", encoding="utf-8") as f:
        return any(row[0] == doctor_id for row in csv.reader(f) if row)


# ─── Templates ───────────────────────────────────────────────────────────────
BASE_STYLE = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e8eaf0;
    --muted: #6b7280;
    --accent: #4f8ef7;
    --approve: #22c55e;
    --edit: #f59e0b;
    --decline: #ef4444;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 40px;
    width: 100%;
    max-width: 480px;
    animation: fadeUp .4s ease both;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .logo {
    font-family: 'Unbounded', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: .08em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 32px;
  }

  h1 {
    font-family: 'Unbounded', sans-serif;
    font-size: 20px;
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 8px;
  }

  p.sub {
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 28px;
  }

  label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: 8px;
  }

  input[type="text"] {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    padding: 14px 16px;
    outline: none;
    transition: border-color .2s;
  }

  input[type="text"]:focus { border-color: var(--accent); }

  .btn-primary {
    display: block;
    width: 100%;
    margin-top: 16px;
    padding: 14px;
    background: var(--accent);
    color: #fff;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 500;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: opacity .2s, transform .1s;
  }

  .btn-primary:hover { opacity: .88; }
  .btn-primary:active { transform: scale(.98); }

  .photo-wrap {
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 28px;
    border: 1px solid var(--border);
    background: var(--bg);
    aspect-ratio: 3/4;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .photo-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .actions { display: flex; flex-direction: column; gap: 10px; }

  .btn-action {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 400;
    cursor: pointer;
    transition: border-color .2s, background .2s, transform .1s;
    text-align: left;
  }

  .btn-action:hover { border-color: var(--accent); background: rgba(79,142,247,.07); }
  .btn-action:active { transform: scale(.98); }
  .btn-action .icon { font-size: 18px; flex-shrink: 0; }

  .error {
    background: rgba(239,68,68,.1);
    border: 1px solid rgba(239,68,68,.3);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    color: #fca5a5;
    margin-top: 14px;
  }

  .doctor-id {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 20px;
  }

  .doctor-id span {
    color: var(--accent);
    font-weight: 500;
  }
</style>
"""

ENTER_ID_HTML = """
<!DOCTYPE html><html><head>""" + BASE_STYLE + """
<title>Медблок — согласование фото</title>
</head><body>
<div class="card">
  <div class="logo">Медблок</div>
  <h1>Согласование фотографии</h1>
  <p class="sub">Введите ваш ID, чтобы увидеть фото, подготовленное для размещения.</p>
  <form method="POST" action="/photo">
    <label for="doctor_id">Ваш ID</label>
    <input type="text" id="doctor_id" name="doctor_id"
           placeholder="Например: 1647495" autocomplete="off" autofocus>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <button type="submit" class="btn-primary">Продолжить →</button>
  </form>
</div>
</body></html>
"""

PHOTO_HTML = """
<!DOCTYPE html><html><head>""" + BASE_STYLE + """
<title>Медблок — ваше фото</title>
</head><body>
<div class="card">
  <div class="logo">Медблок</div>
  <h1>Ваше фото</h1>
  <p class="sub">Рассмотрите фотографию и выберите решение.</p>
  <div class="doctor-id">ID: <span>{{ doctor_id }}</span></div>
  <div class="photo-wrap">
    <img src="{{ image_url }}" alt="Ваше фото" onerror="this.style.display='none'">
  </div>
  <form method="POST" action="/respond">
    <input type="hidden" name="doctor_id" value="{{ doctor_id }}">
    <div class="actions">
      <button type="submit" name="status" value="approve" class="btn-action">
        <span class="icon">✅</span> Да, нравится — можно размещать
      </button>
      <button type="submit" name="status" value="edit" class="btn-action">
        <span class="icon">✏️</span> Нужны правки
      </button>
      <button type="submit" name="status" value="decline" class="btn-action">
        <span class="icon">❌</span> Отказываюсь от размещения
      </button>
    </div>
  </form>
</div>
</body></html>
"""

DONE_HTML = """
<!DOCTYPE html><html><head>""" + BASE_STYLE + """
<title>Медблок — ответ принят</title>
</head><body>
<div class="card" style="text-align:center;">
  <div class="logo">Медблок</div>
  <div style="font-size:48px; margin-bottom:20px;">{{ icon }}</div>
  <h1>{{ title }}</h1>
  <p class="sub" style="margin-top:10px;">{{ message }}</p>
</div>
</body></html>
"""

ALREADY_HTML = """
<!DOCTYPE html><html><head>""" + BASE_STYLE + """
<title>Медблок</title>
</head><body>
<div class="card" style="text-align:center;">
  <div class="logo">Медблок</div>
  <div style="font-size:48px; margin-bottom:20px;">🔒</div>
  <h1>Ответ уже принят</h1>
  <p class="sub" style="margin-top:10px;">Вы уже отправили решение по этому фото. Если нужно изменить — свяжитесь с администратором.</p>
</div>
</body></html>
"""

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return render_template_string(ENTER_ID_HTML, error=None)


@app.route("/photo", methods=["POST"])
def photo():
    doctor_id = request.form.get("doctor_id", "").strip()

    if not doctor_id:
        return render_template_string(ENTER_ID_HTML, error="Введите ваш ID.")

    if doctor_id not in DOCTORS:
        return render_template_string(ENTER_ID_HTML, error="ID не найден. Проверьте правильность ввода.")

    if already_responded(doctor_id):
        return render_template_string(ALREADY_HTML)

    image_url = get_direct_image_url(DOCTORS[doctor_id])
    return render_template_string(PHOTO_HTML, doctor_id=doctor_id, image_url=image_url)


@app.route("/respond", methods=["POST"])
def respond():
    doctor_id = request.form.get("doctor_id", "").strip()
    status = request.form.get("status", "").strip()

    if not doctor_id or doctor_id not in DOCTORS or status not in STATUS_LABELS:
        return redirect(url_for("index"))

    if already_responded(doctor_id):
        return render_template_string(ALREADY_HTML)

    save_response(doctor_id, status)

    messages = {
        "approve": ("✅", "Спасибо!", "Ваше согласие зафиксировано. Фото будет размещено."),
        "edit":    ("✏️", "Принято!", "Мы получили запрос на правки. Скоро свяжемся с вами."),
        "decline": ("❌", "Принято!", "Отказ зафиксирован. Фото размещено не будет."),
    }
    icon, title, message = messages[status]
    return render_template_string(DONE_HTML, icon=icon, title=title, message=message)


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)

from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Football Predictor</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #07110d;
    color: white;
}
header {
    background: #10291c;
    padding: 24px 15px;
    text-align: center;
    border-bottom: 2px solid #24d477;
}
h1 { color: #36e68b; font-size: 25px; }
header p { color: #c4d8cb; }
main { max-width: 600px; margin: auto; padding: 18px; }
.card {
    background: #12251b;
    border: 1px solid #254b35;
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 18px;
}
h2 { color: #49e995; font-size: 19px; }
input, button {
    width: 100%;
    padding: 13px;
    margin-top: 10px;
    border-radius: 9px;
    font-size: 16px;
}
input {
    background: #07110d;
    border: 1px solid #42664f;
    color: white;
}
button {
    background: #27d879;
    color: #062313;
    border: none;
    font-weight: bold;
}
.result {
    margin-top: 15px;
    line-height: 1.9;
    color: #d9f8e5;
}
footer {
    text-align: center;
    color: #91a99a;
    padding: 20px;
    font-size: 13px;
}
</style>
</head>
<body>
<header>
    <h1>⚽ AI FOOTBALL</h1>
    <p>توقّع المباراة وحلّل الفريقين</p>
</header>
<main>
    <section class="card">
        <h2>🔎 تحليل مباراة</h2>
        <form action="/analyze" method="get">
            <input name="home" placeholder="الفريق الأول" required>
            <input name="away" placeholder="الفريق الثاني" required>
            <button type="submit">تحليل المباراة ⚡</button>
        </form>
        {% if home %}
        <div class="result">
            <h3>{{ home }} ضد {{ away }}</h3>
            <p>{{ message }}</p>
        </div>
        {% endif %}
    </section>
    <section class="card">
        <h2>📅 المباريات القادمة</h2>
        <p>سيتم ربط هذا القسم ببيانات المباريات الحقيقية لاحقاً.</p>
    </section>
    <section class="card">
        <h2>🔴 النتائج المباشرة</h2>
        <p>سيتم تفعيل النتائج المباشرة بعد ربط مصدر البيانات.</p>
    </section>
</main>
<footer>AI Football Predictor · التوقعات ليست نتائج مضمونة</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/analyze")
def analyze():
    home = __import__("flask").request.args.get("home", "").strip()
    away = __import__("flask").request.args.get("away", "").strip()

    if not home or not away:
        return "اكتب اسم الفريقين", 400

    return render_template_string(
        HTML,
        home=home,
        away=away,
        message="هذه نسخة تجريبية. تحليل الذكاء الاصطناعي يحتاج ربط بيانات حقيقية."
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, request, redirect, render_template_string
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        note = request.form["note"]
        cur.execute("INSERT INTO notes (content) VALUES (%s)", (note,))
        db.commit()

    cur.execute("SELECT id, content FROM notes")
    notes = cur.fetchall()
    cur.close()
    db.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quick Notes</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white flex justify-center items-center min-h-screen">
        <div class="bg-gray-800 p-6 rounded-xl w-full max-w-md">
            <h2 class="text-2xl font-bold mb-4 text-indigo-400">Quick Notes</h2>
            <form method="POST" class="flex gap-2 mb-4">
                <input name="note" required class="flex-1 p-2 rounded bg-gray-700">
                <button class="bg-indigo-600 px-4 rounded">Add</button>
            </form>
            <ul class="space-y-2">
                {% for n in notes %}
                <li class="flex justify-between bg-gray-700 p-2 rounded">
                    {{ n[1] }}
                    <a href="/delete/{{ n[0] }}" class="text-red-400">X</a>
                </li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    """, notes=notes)

@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM notes WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()
    return redirect("/")

if __name__ == "__main__":
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content TEXT
        )
    """)
    db.commit()
    cur.close()
    db.close()

    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    long_url TEXT NOT NULL,
                    short_code TEXT NOT NULL UNIQUE
                )''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    shorturl = None
    host = request.host_url.rstrip('/')
    
    if request.method == 'POST':
        long_url = request.form['long_url']
        if not long_url:
            error = "Please enter a URL"
            return render_template('index.html', error=error, host=host)
            
        try:
            short_code = generate_short_code()
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
            conn.commit()
            conn.close()
            shorturl = f"/{short_code}"
        except sqlite3.IntegrityError:
            # If the short code already exists, try again
            return home()
        except Exception as e:
            error = "An error occurred. Please try again."
            
    return render_template('index.html', error=error, shorturl=shorturl, host=host)

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()
    if result:
        return redirect(result[0])
    return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

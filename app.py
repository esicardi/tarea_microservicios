from flask import Flask, request, jsonify, Response
import sqlite3
import uuid
import datetime

app = Flask(__name__)
DATABASE = 'chucknorris.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                body TEXT
            )
        ''')
        
        # Check if there are already facts in the table
        cursor.execute('SELECT COUNT(*) FROM facts')
        count = cursor.fetchone()[0]
        
        if count < 10:
            # Insert 10 initial facts if the table is empty or has less than 10 facts
            initial_facts = [
                "Chuck Norris can divide by zero.",
                "Chuck Norris counted to infinity. Twice.",
                "Chuck Norris can hear sign language.",
                "Chuck Norris can slam a revolving door.",
                "Chuck Norris can speak Braille.",
                "Chuck Norris can unscramble an egg.",
                "Chuck Norris doesn't wear a watch. HE decides what time it is.",
                "Chuck Norris can build a snowman out of rain.",
                "Chuck Norris once kicked a horse in the chin. Its descendants are known today as Giraffes.",
                "Chuck Norris can divide by zero."
            ]
            
            timestamp = datetime.datetime.now().isoformat()
            for fact in initial_facts:
                cursor.execute('INSERT INTO facts (timestamp, body) VALUES (?, ?)', (timestamp, fact))
            
            conn.commit()

@app.route('/', methods=['GET'])
def welcome():
    return "¡Bienvenido al servidor de facts!\n"

@app.route('/facts', methods=['POST'])
def create_fact():
    data = request.json
    body = data.get('text')

    if not body:
        return jsonify({"error": "Text field is required"}), 400

    timestamp = datetime.datetime.now().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO facts (timestamp, body) VALUES (?, ?)',
                       (timestamp, body))
        fact_id = cursor.lastrowid
        conn.commit()

    return jsonify({"inserted_id": fact_id}), 201

@app.route('/facts', methods=['GET'])
def get_facts():
    since = request.args.get('since')
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if since:
            cursor.execute('SELECT * FROM facts WHERE timestamp >= ?', (since,))
        else:
            cursor.execute('SELECT * FROM facts')
        rows = cursor.fetchall()

    facts = [{"id": row[0], "fact": row[2], "timestamp": row[1]} for row in rows]
    return jsonify(facts), 200

@app.route('/facts/random', methods=['GET'])
def get_random_fact():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()

    if row:
        fact = {"id": row[0], "fact": row[2], "timestamp": row[1]}
        return jsonify(fact), 200
    else:
        return jsonify({"error": "No facts available"}), 404

@app.route('/facts/<int:fact_id>', methods=['GET'])
def get_fact_by_id(fact_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE id = ?', (fact_id,))
        row = cursor.fetchone()

    if row:
        fact = {"id": row[0], "fact": row[2], "timestamp": row[1]}
        return jsonify(fact), 200
    else:
        return jsonify({"error": "Fact not found"}), 404

@app.route('/facts/date/<string:date>', methods=['GET'])
def get_facts_by_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE DATE(timestamp) = ?', (date,))
        rows = cursor.fetchall()

    facts = [{"id": row[0], "text": row[2], "timestamp": row[1]} for row in rows]
    return jsonify(facts), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=48080)

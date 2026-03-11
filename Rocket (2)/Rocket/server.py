import os
import json
import uuid
import asyncio
import psycopg2
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fo-catalyst-dashboard-2024')

DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalyst_reports (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50) NOT NULL,
            rank VARCHAR(10),
            ticker VARCHAR(50),
            direction VARCHAR(20),
            catalyst TEXT,
            adjusted_impact_usd BIGINT,
            confidence_pct INTEGER,
            time_horizon VARCHAR(50),
            summary TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', domain=DOMAIN)

@app.route('/api/catalysts', methods=['GET'])
def get_catalysts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT run_id, rank, ticker, direction, catalyst,
               adjusted_impact_usd, confidence_pct, time_horizon, summary, created_at
        FROM catalyst_reports
        ORDER BY created_at DESC
        LIMIT 50
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    catalysts = []
    for row in rows:
        catalysts.append({
            'run_id': row[0],
            'rank': row[1],
            'ticker': row[2],
            'direction': row[3],
            'catalyst': row[4],
            'adjusted_impact_usd': row[5],
            'confidence_pct': row[6],
            'time_horizon': row[7],
            'summary': row[8],
            'created_at': row[9].isoformat() if row[9] else None
        })

    return jsonify({'catalysts': catalysts, 'count': len(catalysts)})

@app.route('/api/catalysts/latest', methods=['GET'])
def get_latest_run():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT run_id, MIN(created_at) as run_time
        FROM catalyst_reports
        GROUP BY run_id
        ORDER BY run_time DESC
        LIMIT 1
    """)
    latest = cur.fetchone()

    if not latest:
        cur.close()
        conn.close()
        return jsonify({'catalysts': [], 'run_id': None, 'run_time': None})

    run_id = latest[0]
    run_time = latest[1]

    cur.execute("""
        SELECT rank, ticker, direction, catalyst,
               adjusted_impact_usd, confidence_pct, time_horizon, summary
        FROM catalyst_reports
        WHERE run_id = %s
        ORDER BY rank
    """, (run_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    catalysts = []
    for row in rows:
        catalysts.append({
            'rank': row[0],
            'ticker': row[1],
            'direction': row[2],
            'catalyst': row[3],
            'adjusted_impact_usd': row[4],
            'confidence_pct': row[5],
            'time_horizon': row[6],
            'summary': row[7]
        })

    return jsonify({
        'catalysts': catalysts,
        'run_id': run_id,
        'run_time': run_time.isoformat() if run_time else None
    })

@app.route('/api/catalysts/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT run_id, MIN(created_at) as run_time, COUNT(*) as catalyst_count
        FROM catalyst_reports
        GROUP BY run_id
        ORDER BY run_time DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    runs = []
    for row in rows:
        runs.append({
            'run_id': row[0],
            'run_time': row[1].isoformat() if row[1] else None,
            'catalyst_count': row[2]
        })

    return jsonify({'runs': runs})

@app.route('/api/catalysts/run/<run_id>', methods=['GET'])
def get_run(run_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT rank, ticker, direction, catalyst,
               adjusted_impact_usd, confidence_pct, time_horizon, summary, created_at
        FROM catalyst_reports
        WHERE run_id = %s
        ORDER BY rank
    """, (run_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    catalysts = []
    for row in rows:
        catalysts.append({
            'rank': row[0],
            'ticker': row[1],
            'direction': row[2],
            'catalyst': row[3],
            'adjusted_impact_usd': row[4],
            'confidence_pct': row[5],
            'time_horizon': row[6],
            'summary': row[7],
            'created_at': row[8].isoformat() if row[8] else None
        })

    return jsonify({'catalysts': catalysts, 'run_id': run_id})

@app.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    try:
        from test import think_then_answer_then_reflect
        from signal123 import SQL

        raw_data = SQL()
        if not raw_data:
            return jsonify({'error': 'No signal data available in database'}), 400

        user_input = f"""
        Event Data:
        - Time: {raw_data[0]}
        - Current Exchange Rate: {raw_data[2]}
        - Exchange Rate Last Month: {raw_data[3]}
        - Change Percentage: {raw_data[4]}
        - Is Significant: {raw_data[5]}
        - Mechanism: {raw_data[6]}
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(think_then_answer_then_reflect(user_input))
        loop.close()

        run_id = str(uuid.uuid4())[:8]
        conn = get_db_connection()
        cur = conn.cursor()
        catalysts_saved = 0

        if hasattr(result, 'catalysts'):
            catalysts_list = result.catalysts
        elif isinstance(result, dict) and 'catalysts' in result:
            catalysts_list = result['catalysts']
        else:
            catalysts_list = []

        for cat in catalysts_list:
            if hasattr(cat, 'rank'):
                row = (run_id, str(cat.rank), cat.ticker, cat.direction,
                       cat.catalyst, cat.adjusted_impact_usd, cat.confidence_pct,
                       cat.time_horizon, cat.summary)
            elif isinstance(cat, dict):
                row = (run_id, str(cat.get('rank', '')), cat.get('ticker', ''),
                       cat.get('direction', ''), cat.get('catalyst', ''),
                       cat.get('adjusted_impact_usd', 0), cat.get('confidence_pct', 0),
                       cat.get('time_horizon', ''), cat.get('summary', ''))
            else:
                continue

            cur.execute("""
                INSERT INTO catalyst_reports
                (run_id, rank, ticker, direction, catalyst,
                 adjusted_impact_usd, confidence_pct, time_horizon, summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, row)
            catalysts_saved += 1

        conn.commit()
        cur.close()
        conn.close()

        if catalysts_saved == 0:
            return jsonify({'status': 'warning', 'run_id': run_id,
                            'message': 'Analysis completed but no catalysts were extracted'}), 200

        return jsonify({'status': 'success', 'run_id': run_id, 'catalysts_saved': catalysts_saved})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(DISTINCT run_id) FROM catalyst_reports")
    total_runs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM catalyst_reports")
    total_catalysts = cur.fetchone()[0]

    cur.execute("""
        SELECT direction, COUNT(*) FROM catalyst_reports
        WHERE run_id = (SELECT run_id FROM catalyst_reports ORDER BY created_at DESC LIMIT 1)
        GROUP BY direction
    """)
    direction_counts = dict(cur.fetchall())

    cur.execute("""
        SELECT AVG(confidence_pct) FROM catalyst_reports
        WHERE run_id = (SELECT run_id FROM catalyst_reports ORDER BY created_at DESC LIMIT 1)
    """)
    avg_confidence = cur.fetchone()[0]

    cur.execute("""
        SELECT SUM(ABS(adjusted_impact_usd)) FROM catalyst_reports
        WHERE run_id = (SELECT run_id FROM catalyst_reports ORDER BY created_at DESC LIMIT 1)
    """)
    total_impact = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        'total_runs': total_runs,
        'total_catalysts': total_catalysts,
        'upside_count': direction_counts.get('upside', direction_counts.get('Upside', 0)),
        'downside_count': direction_counts.get('downside', direction_counts.get('Downside', 0)),
        'avg_confidence': round(float(avg_confidence), 1) if avg_confidence else 0,
        'total_impact': int(total_impact) if total_impact else 0
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

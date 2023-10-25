import os

from flask import Flask, jsonify, request

from database import get_database_connection

app = Flask(__name__)


@app.route('/entries', methods=['GET'])
def get_all_entries():
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            sentence = request.args.get('sentence')
            print(f"sentence = {sentence}")
            cursor.execute("""
            SELECT entry_id, title, last_modified_date, NULL AS similarity FROM entry ORDER BY last_modified_date DESC LIMIT 10
            """ if sentence is None else """
            SELECT entry_id, title, last_modified_date, 1 - (embedding <=> (SELECT pgml.embed('intfloat/multilingual-e5-large', %s)::vector)) AS similarity FROM entry ORDER BY similarity DESC LIMIT 10
            """, (sentence,))
            results = cursor.fetchall()
            entries = [
                {
                    "entry_id": row[0],
                    "title": row[1],
                    "last_modified_date": row[2].isoformat(),
                    "similarity": row[3]
                }
                for row in results]
            return jsonify(entries)


@app.route('/entries/<int:entry_id>', methods=['GET'])
def get_single_entry(entry_id):
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT entry_id, title, content, last_modified_date FROM entry WHERE entry_id = %s
            """, (entry_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": "Entry not found"}), 404
            entry = {
                "entry_id": row[0],
                "title": row[1],
                "content": row[2],
                "last_modified_date": row[3].isoformat()
            }
            return jsonify(entry)


@app.route('/entries/<int:entry_id>/similarities', methods=['GET'])
def get_entry_similarities(entry_id):
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT entry_id, title, last_modified_date, 1 - (embedding <=> (SELECT embedding FROM entry WHERE entry_id = %s)) AS similarity FROM entry WHERE entry_id <> %s ORDER BY similarity DESC LIMIT 5
            """, (entry_id, entry_id))
            results = cursor.fetchall()
            entries = [
                {
                    "entry_id": row[0],
                    "title": row[1],
                    "last_modified_date": row[2].isoformat(),
                    "similarity": row[3]
                }
                for row in results]
            return jsonify(entries)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 4000)))

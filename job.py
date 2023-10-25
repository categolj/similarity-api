from datetime import datetime

import psycopg2

from database import get_database_connection, find_directory_with_file, generate_database_url_from_file


def get_last_imported_date(conn):
    with conn.cursor() as cur:
        cur.execute("""
SELECT last_imported_date
FROM metadata
ORDER BY last_imported_date DESC 
LIMIT 1
""")
        result = cur.fetchone()
        return result[0] if result else None


def fetch_new_entries(conn, last_imported_date):
    with conn.cursor() as cur:
        cur.execute("""
SELECT entry_id, title, content, last_modified_date 
FROM entry
WHERE tenant_id = '_' AND last_modified_date > %s 
ORDER BY last_modified_date ASC 
LIMIT 300
""", (last_imported_date,))
        return cur.fetchall()


def copy_new_entries_to_target(conn, entries):
    print(f"update entries = {tuple(entry[0] for entry in entries)}")
    with conn.cursor() as cur:
        cur.executemany("""
INSERT INTO entry (entry_id, title, content, last_modified_date)
VALUES (%s, %s, %s, %s)
ON CONFLICT (entry_id) DO UPDATE
    SET title              = EXCLUDED.title,
        content            = EXCLUDED.content,
        last_modified_date = EXCLUDED.last_modified_date
""", entries)


def update_embeddings(conn, entries):
    ids = tuple(entry[0] for entry in entries)
    print(f"update embeddings = {ids}")
    with conn.cursor() as cur:
        cur.execute("""
UPDATE entry SET embedding = pgml.embed('intfloat/multilingual-e5-large', content)::vector WHERE entry_id IN %s
""", (ids,))


def update_last_imported_date(conn, last_imported_date):
    with conn.cursor() as cur:
        cur.execute("""
INSERT INTO metadata(last_imported_date) VALUES(%s)
""", (last_imported_date,))


def generate_source_database_url():
    target_directory = find_directory_with_file("type", "postgresql-source")
    return generate_database_url_from_file(target_directory)


def get_source_database_connection():
    conn = psycopg2.connect(generate_source_database_url())
    return conn


def main():
    # インポート元のデータベースに接続
    with get_source_database_connection() as source_conn:
        # インポート先のデータベースに接続
        with get_database_connection() as target_conn:
            # 最後にインポートされた日付を取得
            last_imported_date = get_last_imported_date(target_conn)
            if not last_imported_date:
                last_imported_date = datetime.min

            print(f"last_imported_date = {last_imported_date}")
            # インポート元から新しいエントリを取得
            entries = fetch_new_entries(source_conn, last_imported_date)

            if entries:
                # 新しいエントリをインポート先にコピー
                copy_new_entries_to_target(target_conn, entries)
                # embeddingを更新
                update_embeddings(target_conn, entries)

                # 最新の last_modified_date を取得
                newest_date = max(entry[-1] for entry in entries)

                # metadataテーブルの last_imported_date を更新
                update_last_imported_date(target_conn, newest_date)
                target_conn.commit()


if __name__ == '__main__':
    main()

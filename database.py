import os

import psycopg2


def find_directory_with_file_from_root_dir(root_dir, filename, content):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if filename in filenames:
            file_path = os.path.join(dirpath, filename)
            with open(file_path, 'r') as file:
                if content == file.read():
                    return dirpath
    return None


def find_directory_with_file(filename, content):
    root_directory = os.environ.get('SERVICE_BINDING_ROOT') or os.getcwd()
    return find_directory_with_file_from_root_dir(root_directory, filename, content)


def get_file_content(dirpath, filename):
    file_path = os.path.join(dirpath, filename)
    with open(file_path, 'r') as file:
        return file.read().strip()


def generate_database_url_from_file(target_directory):
    username = get_file_content(target_directory, "username")
    password = get_file_content(target_directory, "password")
    host = get_file_content(target_directory, "host")
    port = get_file_content(target_directory, "port")
    database = get_file_content(target_directory, "database")
    print(f"Connecting postgresql://{username}:****@{host}:{port}/{database} ...")
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


def generate_database_url():
    target_directory = find_directory_with_file("type", "postgresql")
    return generate_database_url_from_file(target_directory)


DATABASE_URL = generate_database_url()


def get_database_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

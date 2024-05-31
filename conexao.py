import os
import sqlite3

# CONECTAR AO BANCO DE DADOS

def get_db_connection():
    if not os.path.exists('database'):
        os.makedirs('database')
    if not os.path.exists('database/tecblog.db'):
        conn = sqlite3.connect('database/tecblog.db')
        create_tables(conn)
    else:
        conn = sqlite3.connect('database/tecblog.db')
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn

# CRIAÇÃO DAS TABELAS

def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        senha TEXT NOT NULL
    )
''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS post (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date_posted TEXT NOT NULL,
        img BLOB,
        content TEXT NOT NULL,
        link TEXT NOT NULL
    )
''')
    
    inserir(conn)
    conn.commit()

def inserir(conn):
    usuarios = conn.execute('SELECT * FROM usuario').fetchall()
    if not usuarios:
        conn.execute('''
        INSERT INTO usuario(nome, email, senha)
        values("usuario", "usuario@tecblog.com.br", "1234")
''')    
        
        
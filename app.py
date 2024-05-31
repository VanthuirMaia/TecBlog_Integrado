import os
import sqlite3
import base64
import datetime
from flask import Flask, url_for, render_template, request, redirect, session, flash, abort
from conexao import get_db_connection, create_tables
from functools import wraps
from werkzeug.utils import secure_filename

if os.environ.get('VIRTUAL_ENV') is None:
    print("A Virtual enviroment não esta ativa. Ativando...")
    os.system('venv/Scripts/activate')

# CRIANDO O OBJETO APP
app = Flask(__name__, static_folder='static' )

app.secret_key = 'chavepara rodar'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# INÍCIO DAS ROTAS

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    return datetime.datetime.strptime(value, '%Y-%m-%d').strftime(format)

# ROTA PRINCIPAL
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    conn.close()
    
    # Reverte a ordem das postagens para que a mais recente fique no topo
    posts = list(reversed(posts))
    
    return render_template('site/index.html', posts=posts)



@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    create_tables(conn)
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = ? and senha = ?', (email,senha))
        
        usuario = cursor.fetchone()
        #print(f'SELECT * FROM usuario WHERE email = {email} and senha = {senha}')
        conn.close()
        if usuario:
            #print(usuario)
            session['email'] = email
            return redirect('/dashboard')
        else:
            return render_template('admin/login.html', error='Credenciais inválidas')
    return render_template('admin/login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# ROTAS DE ADMINISTRAÇÃO

@app.route('/admin')
@login_required
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    conn.close()
    return render_template('admin/index.html', posts=posts)




@app.route('/adicionar_post', methods=['GET', 'POST'])
@login_required
def adicionar_post():
    if request.method == 'POST':
        title = request.form['title']
        date_posted = request.form['date_posted']
        content = request.form['content']
        link = request.form['link']
        img = request.files['image']

        if img:
            img_base64 = base64.b64encode(img.read()).decode('utf-8')
        else:
            img_base64 = ''

        conn = get_db_connection()
        conn.execute('INSERT INTO post (title, date_posted, img, content, link) VALUES (?, ?, ?, ?, ?)',
                     (title, date_posted, img_base64, content, link))
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))

    return render_template('admin/adicionar_post.html')


@app.route('/editar_post/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM post WHERE id = ?', (id,)).fetchone()
    if not post:
        flash('Postagem não encontrada.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        link = request.form['link']
        image = request.files['image']

        if not title or not content:
            flash('Título e conteúdo são obrigatórios.', 'error')
        else:
            if image and image.filename != '':
                img_base64 = base64.b64encode(image.read()).decode('utf-8')
                conn.execute('UPDATE post SET title = ?, content = ?, link = ?, img = ? WHERE id = ?',
                             (title, content, link, img_base64, id))
            else:
                conn.execute('UPDATE post SET title = ?, content = ?, link = ? WHERE id = ?',
                             (title, content, link, id))
            conn.commit()
            flash('Postagem editada com sucesso!', 'success')
            conn.close()
            return redirect(url_for('admin'))

    conn.close()
    return render_template('admin/editar_post.html', post=post)


@app.route('/excluir_post/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir_post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM post WHERE id = ?', (id,)).fetchone()
    
    if not post:
        flash('Postagem não encontrada.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        conn.execute('DELETE FROM post WHERE id = ?', (id,))
        conn.commit()
        flash('Postagem excluída com sucesso!', 'success')
        conn.close()
        return redirect(url_for('admin'))
    
    conn.close()
    return render_template('admin/excluir_post.html', post=post)






if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, send_file
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from math import ceil

app = Flask(__name__)

# Banco de dados em memória (simples)
produtos = []

# Função para filtrar produtos
def filtrar_produtos(query):
    return [p for p in produtos if query.lower() in p['nome'].lower()]

# Função para aplicar paginação
def paginar_produtos(produtos, page, per_page=5):
    start = (page - 1) * per_page
    end = start + per_page
    return produtos[start:end]

@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.form.get('query', '')
    page = request.args.get('page', 1, type=int)

    # Filtro por consulta
    produtos_filtrados = filtrar_produtos(query) if query else produtos
    total_produtos = len(produtos_filtrados)
    
    # Ajuste na paginação
    produtos_paginados = paginar_produtos(produtos_filtrados, page)

    total_paginas = ceil(total_produtos / 5) if total_produtos > 0 else 1

    return render_template('index.html', 
                           produtos=produtos_paginados, 
                           query=query,
                           page=page, 
                           total_paginas=total_paginas)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    quantidade = int(request.form['quantidade'])
    preco = float(request.form['preco'])
    retirado_por = request.form['retirado_por']
    data_retirada = request.form['data_retirada']
    
    produtos.append({
        'nome': nome,
        'quantidade': quantidade,
        'preco': preco,
        'retirado_por': retirado_por,
        'data_retirada': data_retirada
    })
    return redirect(url_for('index'))

@app.route('/remover/<int:index>')
def remover(index):
    if 0 <= index < len(produtos):
        produtos.pop(index)
    return redirect(url_for('index'))

@app.route('/exportar/excel')
def exportar_excel():
    df = pd.DataFrame(produtos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Estoque')
    output.seek(0)
    return send_file(output, download_name="estoque.xlsx", as_attachment=True)

@app.route('/exportar/pdf')
def exportar_pdf():
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, y, "Relatório de Estoque")

    y -= 40
    c.setFont("Helvetica", 10)
    for produto in produtos:
        linha = (f"Produto: {produto['nome']} | Quantidade: {produto['quantidade']} | "
                 f"Preço: R$ {produto['preco']:.2f} | Retirado por: {produto['retirado_por']} | "
                 f"Data: {produto['data_retirada']}")
        c.drawString(30, y, linha)
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 40

    c.save()
    output.seek(0)
    return send_file(output, download_name="estoque.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

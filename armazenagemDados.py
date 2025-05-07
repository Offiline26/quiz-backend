from flask import Flask, request, jsonify
import oracledb

app = Flask(__name__)

# Configurar conexão (ajuste user, password, host e service_name conforme seu ambiente)
import os
conn = oracledb.connect(
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    dsn=os.environ["ORACLE_DSN"]
)


@app.route('/quiz', methods=['POST'])
def salvar_resposta():
    dados = request.json
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO quiz_respostas (nome, idade, pontos, util, data_envio)
            VALUES (:1, :2, :3, :4, SYSTIMESTAMP)
        """, (dados['nome'], dados['idade'], dados['pontos'], dados.get('util')))
        conn.commit()
    return jsonify({"status": "salvo com sucesso"}), 201

@app.route('/quiz', methods=['GET'])
def listar_respostas():
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT nome, idade, pontos, util, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') AS data_envio
            FROM quiz_respostas
            ORDER BY data_envio DESC
        """)
        colunas = [col[0].lower() for col in cursor.description]
        respostas = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        return jsonify(respostas)

if __name__ == '__main__':
    app.run(debug=True)

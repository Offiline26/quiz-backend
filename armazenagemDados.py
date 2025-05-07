from flask import Flask, request, jsonify
from flask_cors import CORS
import oracledb
import os

app = Flask(__name__)
CORS(app)

# Conexão com Oracle
def get_connection():
    return oracledb.connect(
        user=os.environ.get("ORACLE_USER"),
        password=os.environ.get("ORACLE_PASSWORD"),
        dsn=os.environ.get("ORACLE_DSN")
    )

@app.route('/quiz', methods=['POST'])
def salvar_resposta():
    dados = request.json
    try:
        with get_connection().cursor() as cursor:
            cursor.execute("""
                INSERT INTO quiz_respostas (nome, idade, pontos, util, data_envio)
                VALUES (:1, :2, :3, :4, SYSTIMESTAMP)
            """, (dados['nome'], dados['idade'], dados['pontos'], dados.get('util')))
            cursor.connection.commit()
        return jsonify({"status": "salvo com sucesso"}), 201
    except Exception as e:
        print("Erro ao salvar:", e)
        return jsonify({"erro": "Erro ao salvar dados"}), 500

@app.route('/quiz', methods=['GET'])
def listar_respostas():
    try:
        with get_connection().cursor() as cursor:
            cursor.execute("""
                SELECT nome, idade, pontos, util, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') AS data_envio
                FROM quiz_respostas
                ORDER BY data_envio DESC
            """)
            colunas = [col[0].lower() for col in cursor.description]
            respostas = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        return jsonify(respostas)
    except Exception as e:
        print("Erro ao carregar dados:", e)
        return jsonify([]), 500

if __name__ == '__main__':
    # Porta obrigatória para ambientes como o Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

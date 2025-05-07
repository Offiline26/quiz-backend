from flask import Flask, request, jsonify
from flask_cors import CORS
import oracledb
import os

app = Flask(__name__)
CORS(app)

# Função para abrir uma nova conexão a cada requisição
def get_connection():
    try:
        return oracledb.connect(
            user=os.environ["ORACLE_USER"],
            password=os.environ["ORACLE_PASSWORD"],
            dsn=os.environ["ORACLE_DSN"]
        )
    except Exception as e:
        print("Erro ao conectar no Oracle:", e)
        raise

# Rota para salvar a resposta do quiz
@app.route('/quiz', methods=['POST'])
def salvar_resposta():
    dados = request.json
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO quiz_respostas (nome, idade, pontos, util, data_envio)
                    VALUES (:1, :2, :3, :4, SYSTIMESTAMP)
                """, (dados['nome'], dados['idade'], dados['pontos'], dados.get('util')))
                conn.commit()
        return jsonify({"status": "salvo com sucesso"}), 201
    except Exception as e:
        print("Erro ao salvar:", e)
        return jsonify({"erro": "Erro ao salvar dados"}), 500

# Rota para listar as respostas
@app.route('/quiz', methods=['GET'])
def listar_respostas():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
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

# Início da aplicação
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Porta exigida pela Render
    app.run(host='0.0.0.0', port=port)

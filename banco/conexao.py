"""
import psycopg2

try:
    conexao = psycopg2.connect(
         dbname="brokerdb",
         user="postgres",
         password="sua_senha",
         host="localhost",
         port="5432"
    )
    cursor=conexao.cursor()
    print("conexao bem sucedida")
except Exception as erro:
    print(f"erro na conexao: {erro}")
"""
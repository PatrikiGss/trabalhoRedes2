-- Criação do banco de dados
CREATE DATABASE brokerdb;

\connect brokerdb

-- Criação da tabela de tópicos
CREATE TABLE topicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL
);

-- Criação da tabela de mensagens
CREATE TABLE mensagens (
    id SERIAL PRIMARY KEY,
    topico_id INTEGER REFERENCES topicos(id) ON DELETE CASCADE,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mensagem opcional para verificar que deu certo
SELECT 'Banco de dados, tabelas de tópicos e mensagens criados com sucesso!' AS status;

--para rodar no terminal execute: psql -U postgres -f broker.sql


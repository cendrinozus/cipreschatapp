-- Script d'initialisation MySQL pour le chatbot entreprise
-- Exécuter : mysql -u root -p < scripts/init_db.sql

CREATE DATABASE IF NOT EXISTS chatbot_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'chatbot'@'localhost' IDENTIFIED BY 'chatbot_pass';
GRANT ALL PRIVILEGES ON chatbot_db.* TO 'chatbot'@'localhost';
FLUSH PRIVILEGES;

USE chatbot_db;

-- Les tables sont créées automatiquement par SQLAlchemy au démarrage Flask.
-- Ce script crée uniquement la base et l'utilisateur.

-- Optionnel : insérer un admin par défaut
-- (mot de passe : Admin1234! — À CHANGER en production)
-- Le hash bcrypt ci-dessous correspond à "Admin1234!"
-- INSERT INTO users (username, email, password, role) VALUES
-- ('admin', 'admin@entreprise.com',
--  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lr.wqhDLHEoH9zBqK',
--  'admin');

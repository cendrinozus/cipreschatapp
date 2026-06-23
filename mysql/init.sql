-- MySQL Docker crée automatiquement :
--   - La base (MYSQL_DATABASE)
--   - L'utilisateur MYSQL_USER@'%' avec droits sur la base
--
-- Ce fichier assure l'encodage UTF-8 MB4 (déjà par défaut sous MySQL 8).

ALTER DATABASE chatbot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- SaigonBite OFDH: create the database and its owner (PostgreSQL).
-- Run once as a PostgreSQL superuser, for example:  psql -U postgres -f sql/create_database.sql
-- The password below is for local development only.
CREATE USER saigonbite WITH PASSWORD 'saigonbite';
CREATE DATABASE saigonbite OWNER saigonbite ENCODING 'UTF8';
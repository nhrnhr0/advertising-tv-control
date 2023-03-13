sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl

sudo -u postgres psql

CREATE DATABASE kehiladb;

CREATE USER djangouser WITH PASSWORD 'WYCZY49xe9pcCV47E5EC';

ALTER ROLE djangouser SET client_encoding TO 'utf8';

ALTER ROLE djangouser SET default_transaction_isolation TO 'read committed';

ALTER ROLE djangouser SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE kehiladb TO djangouser;

\q




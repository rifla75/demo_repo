sudo dnf install vscode
    psql --version


    mkdir -p .venv
    ls
    ls -la
    python3 -m venv /.venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip3 install -r requirements.txt
    sudo -u postgres psql


python3 --version
pg_isready
which code

sudo dnf install -y python3 python3-pip python3-qt5 python3-qt5-devel \
                    postgresql postgresql-server postgresql-contrib

sudo dnf install -y code


# ===== 1. СИСТЕМНЫЕ ПАКЕТЫ =====
sudo dnf install -y python3 python3-pip python3-qt5 python3-qt5-devel \
                    postgresql postgresql-server postgresql-contrib

# ===== 2. VS CODE =====
sudo dnf install -y code

# ===== 3. POSTGRESQL =====
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
sleep 2
pg_isready

# ===== 4. ПРОЕКТ С ФЛЕШКИ =====
cp -r /run/media/$USER/*/chudo_obuv ~/
cd ~/chudo_obuv

# ===== 5. VENV + БИБЛИОТЕКИ =====
python3 -m venv .venv
source .venv/bin/activate
pip install psycopg2-binary openpyxl

# ===== 6. СОЗДАТЬ БД =====
sudo -u postgres psql << 'EOF'
CREATE DATABASE chudo_obuv;
CREATE USER obuv_user WITH PASSWORD 'obuv_pass';
GRANT ALL PRIVILEGES ON DATABASE chudo_obuv TO obuv_user;
\c chudo_obuv
GRANT ALL ON SCHEMA public TO obuv_user;
\q
EOF

# ===== 7. СХЕМА + SEED =====
PGPASSWORD=obuv_pass psql -h localhost -U obuv_user -d chudo_obuv -f db/schema.sql
PGPASSWORD=obuv_pass psql -h localhost -U obuv_user -d chudo_obuv -f db/seed.sql

# ===== 8. ИМПОРТ XLSX =====
python3 -m db.import_data

# ===== 9. ЗАПУСК =====
python3 main.py

                    

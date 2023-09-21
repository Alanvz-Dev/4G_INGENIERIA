START_TIME=$(date +%s)
export PGPASSWORD='58877216/Abca1373';
time psql --host=192.168.1.2 --port=5438 --username=odoo11 --echo-all --dbname=4G_INGENIERIA < /home/dev-odoo/Odoo11Nomina4.0.6/Postgres/4G_INGENIERIA3.sql
END_TIME=$(date +%s)
echo "Restore took $(($END_TIME - $START_TIME)) seconds..."

#GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA 4G_INGENIERIA TO odoo11;

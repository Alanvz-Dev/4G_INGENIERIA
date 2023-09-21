START_TIME=$(date +%s)
time pg_dump --username=odoo11 --dbname=4G_INGENIERIA --no-owner  --verbose > 4G_INGENIERIA3.sql
END_TIME=$(date +%s)
echo "Backup took $(($END_TIME - $START_TIME)) seconds..."


# tar -czvf 4G_INGENIERIA.tar.gz



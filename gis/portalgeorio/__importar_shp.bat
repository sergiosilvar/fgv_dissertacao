for %%f in (*.shp) do shp2pgsql -W LATIN1 -I -s 29193:4326 %%f pgr_%%~nf > pgr_%%~nf.sql
for %%f in (*.sql) do psql -d postgresql://postgres:1234@localhost/zap -f %%f
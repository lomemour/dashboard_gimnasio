#!/bin/bash
# Exporta los tres CSV del dashboard desde la base FINAL del proyecto.
# Uso (desde la carpeta dashboard_gimnasio):  bash exportar_csv_final.sh
MYSQL=/usr/local/mysql/bin/mysql
USUARIO=root
read -s -p "Contrasena de MySQL: " MYSQL_PWD; echo
export MYSQL_PWD
mkdir -p datos
rm -f datos/*.csv

exportar () {
  $MYSQL -u "$USUARIO" --default-character-set=utf8mb4 gimnasio_db --batch --raw -e "$2" | tr '\t' ',' > "datos/$1"
  echo "datos/$1 -> $(($(wc -l < "datos/$1") - 1)) filas"
}

exportar asistencias_mes_disciplina.csv "
SELECT DATE_FORMAT(a.fecha, '%Y-%m') AS mes, d.nombre AS disciplina, COUNT(*) AS asistencias
FROM asistencia a
JOIN sesion s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN clase c ON c.id_clase = a.id_clase
JOIN disciplina d ON d.id_disciplina = c.id_disciplina
WHERE s.estado = 'realizada'
GROUP BY mes, d.nombre ORDER BY mes, d.nombre;"

exportar comportamiento_plan.csv "
SELECT nivel_plan AS plan, socios, visitas_por_socio, minutos_de_anticipacion AS minutos_anticipacion
FROM v_comportamiento_plan;"

exportar canal_edad.csv "
SELECT CASE WHEN fn_edad(so.fecha_nacimiento, a.fecha) < 30 THEN '<30'
            WHEN fn_edad(so.fecha_nacimiento, a.fecha) < 50 THEN '30-49'
            ELSE '50+' END AS rango_edad,
       a.metodo_registro AS metodo, COUNT(*) AS usos
FROM asistencia a JOIN socio so ON so.id_socio = a.id_socio
GROUP BY rango_edad, a.metodo_registro;"

#!/bin/bash
# Exporta las tres consultas a CSV dentro de la carpeta datos/ (sin pasar por Workbench).
# Uso (desde la carpeta dashboard_gimnasio):  bash exportar_csv.sh
MYSQL=/usr/local/mysql/bin/mysql
USUARIO=root
read -s -p "Contrasena de MySQL: " MYSQL_PWD; echo
export MYSQL_PWD
mkdir -p datos

exportar () {  # $1 = archivo, $2 = consulta
  $MYSQL -u "$USUARIO" gimnasio_db --batch --raw -e "$2" | tr '\t' ',' > "datos/$1"
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
SELECT p.nombre AS plan, COUNT(DISTINCT so.id_socio) AS socios,
       ROUND(COUNT(*) / COUNT(DISTINCT so.id_socio), 1) AS visitas_por_socio,
       ROUND(AVG(TIME_TO_SEC(a.hora_llegada)) / 60, 0) AS hora_llegada_min
FROM asistencia a
JOIN sesion s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN socio so ON so.id_socio = a.id_socio
JOIN plan p ON p.id_plan = so.id_plan
WHERE s.estado = 'realizada'
GROUP BY p.nombre;"

exportar canal_plan.csv "
SELECT p.nombre AS plan, a.metodo_registro AS metodo, COUNT(*) AS usos
FROM asistencia a
JOIN sesion s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN socio so ON so.id_socio = a.id_socio
JOIN plan p ON p.id_plan = so.id_plan
WHERE s.estado = 'realizada'
GROUP BY p.nombre, a.metodo_registro;"

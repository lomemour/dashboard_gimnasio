-- Exporta estos tres resultados desde gimnasio_db a CSV y guárdalos en la carpeta datos/
-- (MySQL Workbench: Export results -> CSV, con encabezados, UTF-8, coma como separador)

-- 1) datos/asistencias_mes_disciplina.csv
SELECT DATE_FORMAT(a.fecha, '%Y-%m') AS mes,
       d.nombre                      AS disciplina,
       COUNT(*)                      AS asistencias
FROM asistencia a
JOIN sesion     s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN clase      c ON c.id_clase = a.id_clase
JOIN disciplina d ON d.id_disciplina = c.id_disciplina
WHERE s.estado = 'realizada'
GROUP BY mes, d.nombre
ORDER BY mes, d.nombre;

-- 2) datos/comportamiento_plan.csv
--    hora_llegada_min = hora promedio de llegada, en minutos desde la medianoche (350 = 05:50)
SELECT p.nombre                                             AS plan,
       COUNT(DISTINCT so.id_socio)                          AS socios,
       ROUND(COUNT(*) / COUNT(DISTINCT so.id_socio), 1)     AS visitas_por_socio,
       ROUND(AVG(TIME_TO_SEC(a.hora_llegada)) / 60, 0)      AS hora_llegada_min
FROM asistencia a
JOIN sesion s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN socio so ON so.id_socio = a.id_socio
JOIN plan   p ON p.id_plan = so.id_plan
WHERE s.estado = 'realizada'
GROUP BY p.nombre;

-- 3) datos/canal_plan.csv   (metodo de registro segun el plan del socio)
SELECT p.nombre          AS plan,
       a.metodo_registro AS metodo,
       COUNT(*)          AS usos
FROM asistencia a
JOIN sesion s ON s.id_clase = a.id_clase AND s.fecha = a.fecha
JOIN socio so ON so.id_socio = a.id_socio
JOIN plan   p ON p.id_plan = so.id_plan
WHERE s.estado = 'realizada'
GROUP BY p.nombre, a.metodo_registro;

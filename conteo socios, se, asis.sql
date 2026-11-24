SELECT (SELECT COUNT(*) FROM socio)      AS socios,
       (SELECT COUNT(*) FROM sesion)     AS sesiones,
       (SELECT COUNT(*) FROM asistencia) AS asistencias;
# Comprobaciones del paquete

Comprobado durante la generacion del ZIP, 23 de septiembre de 2026:

- Sintaxis Bash de kimai/run.sh y scripts/smoke-test.sh.
- Analisis de los cinco archivos YAML (incluido el workflow).
- Correspondencia entre las opciones de la app y su esquema.
- Zona horaria predeterminada Europe/Madrid y database_version auto.
- Lista generica de hosts: permite homeassistant.local y localhost;
  no admite sufijos de dominio ajenos ni utiliza un comodin universal.
- Ausencia de la IP de instalacion facilitada en la conversacion.
- 19 pruebas unitarias del detector de versiones, decisiones de publicacion,
  cambios de version principal, reintentos y manifiesto multi-arquitectura.
- 8 pruebas del wrapper en un sistema de archivos temporal aislado: generacion
  de la URL SQL, compatibilidad de version explicita, rechazo de placeholders,
  zona horaria, ausencia de secretos en su salida, persistencia simulada,
  zona invalida y host con protocolo.

Resultado: 27 pruebas locales ejecutadas, 27 correctas, sin pruebas omitidas.

Estas pruebas NO construyen una imagen Docker, NO arrancan MariaDB, NO
se conectan a Home Assistant y NO prueban una migracion de datos reales.
La compilacion y las pruebas reales con MariaDB estan programadas en
GitHub Actions y deben verificarse en su primera ejecucion.

No se ha publicado nada en GitHub/GHCR al generar este ZIP.
No se han descargado aqui los PNG originales de Kimai; los incorpora el
workflow desde el repositorio oficial en la primera publicacion correcta.

Cambios respecto al paquete parcial anterior:

- Se incluyen los archivos completos de la app y del repositorio.
- Se elimina la IP particular de los hosts permitidos.
- Europe/Madrid se configura para el sistema y PHP.
- Se permite detectar la version real de MariaDB con database_version: auto.
- Se validan opciones y se conservan los archivos persistentes al crear enlaces.
- Se desactivan trazas de comandos del entrypoint para reducir exposicion de claves.
- Los scripts deducen el propietario de GHCR desde el contexto de GitHub.
- Se incluyen documentacion, avisos de migracion y traducciones de las opciones.

No mezclar el nuevo config.yaml con un run.sh anterior que no soporte auto.
Si el repositorio ya tiene una release de esa misma version publicada, consulta
Mantenimiento del empaquetado en README.md antes de sustituir codigo: este
workflow no vuelve a publicar un tag existente.

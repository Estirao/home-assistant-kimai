# De la app local al repositorio

No desinstales la app local para probar el repositorio. Home Assistant asigna
identificadores distintos a `local_kimai` y a la app instalada desde GitHub, por
lo que sus volúmenes privados `/data` también son distintos.

## Antes de iniciar la nueva app

1. Publica la imagen en GitHub y verifica que GHCR permite descargarla.
2. Anota la versión instalada de Kimai y guarda, en privado, las opciones reales
   de la app local. Conserva especialmente `app_secret` y la configuración SQL.
3. Detén Kimai y crea una copia de seguridad que incluya Kimai y MariaDB. Guárdala
   fuera de Home Assistant. Si MariaDB sirve también a otras apps, valora el efecto
   de su parada o restauración; no borres ni recrees su base de datos.
4. Identifica y transfiere los contenidos de `kimai-data` y `kimai-plugins` del
   volumen privado de la app antigua al de la nueva. No son los archivos fuente
   que ves en `/local_apps/kimai`. No asumas que estan vacíos porque hay pocos
   registros de horas; podría haber archivos, plantillas o secretos persistidos.
5. Copia las opciones a la app del repositorio, incluyendo las credenciales
   reales, el `app_secret` original y los hosts permitidos. Mantén `Europe/Madrid`.
6. Deja la app local detenida, con arranque y actualización automática desactivados.
   No arranques ambas contra la misma base ni intentando publicar el mismo puerto.
7. Inicia la nueva app, verifica clientes/proyectos/horas, archivos y plugins,
   y prueba la persistencia tras reiniciarla. Después activa su arranque con el sistema,
   pero no la actualización automática.

La transferencia del volumen depende de los accesos y herramientas de tu
instalación. Este paquete no ejecuta una migración ni contiene un comando que
borre la app anterior. Si no puedes localizar/copiar ese volumen, detén el proceso
antes de desinstalar nada y revisa el acceso al backup o al almacenamiento.

La primera imagen del repositorio puede ser una versión de Kimai más reciente
que la local, porque el detector sigue la última estable. Su primer arranque
puede migrar la base de datos. No arranques una app antigua contra esa base para
volver atrás: una reversión necesita restaurar una copia coherente de SQL y archivos.

El hecho de que los tests de GitHub pasen con una MariaDB nueva no comprueba la
migración de tu base actual ni la compatibilidad de tus plugins.

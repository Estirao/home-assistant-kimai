# Kimai para Home Assistant: automatizacion de publicaciones

Preparado para `Estirao/home-assistant-kimai`, rama `main`.

Este paquete es un parche para el repositorio que ya has creado. NO contiene ni
sustituye `kimai/config.yaml`, `kimai/run.sh`, `repository.yaml` ni tu README
principal. NO se debe copiar en `/local_apps` ni en tu Home Assistant.

No se ha modificado tu repositorio desde esta conversacion. Tampoco se ha
compilado ni publicado una imagen real: esos pasos se ejecutaran en GitHub.

## Archivos que debes subir

Extrae el ZIP en tu ordenador y sube su contenido a la raiz del repositorio,
conservando exactamente las carpetas:

```text
.github/workflows/kimai-release.yml
scripts/kimai_release.py
scripts/test_kimai_release.py
scripts/smoke-test.sh
kimai/Dockerfile
LEEME_AUTOMATIZACION.md
```

No subas el ZIP como un archivo ni una carpeta adicional que lo envuelva.
El Dockerfile sustituye el anterior; el resto son archivos nuevos.
Conserva el `run.sh` que ya funciona y el `config.yaml` de la app del repositorio.

En tu `config.yaml` deben estar la version actual y la referencia sin etiqueta:

```yaml
version: "2.67.0"
image: "ghcr.io/estirao/kimai-ha"
```

`2.67.0` es el punto de partida de nuestra conversacion, NO una afirmacion sobre
la ultima version publicada en este momento. El workflow consulta la API en
cada ejecucion y modifica esa linea solo despues de disponer de la imagen.
No cambies `version` manualmente para anunciar una imagen que aun no existe.

No publiques passwords reales, APP_SECRET, opciones de tu instancia, copias de
seguridad, plugins de pago o datos de MariaDB. Los passwords de config.yaml
publico deben seguir siendo marcadores como `CHANGE_ME_DB`.

Si ya has creado otro workflow que publica las mismas imagenes o cambia la
version de Kimai, desactivalo primero para evitar dos publicadores concurrentes.
Este archivo hace la deteccion y la publicacion en un solo workflow.

## Que hace

1. Consulta la ultima release estable oficial de `kimai/kimai`.
2. Acepta cualquier version estable X.Y.Z, incluida una futura 3.x, 4.x, etc.
   Ignora drafts y prereleases; no usa un filtro que empiece por 2.
3. No baja automaticamente la version si la API devuelve una inferior.
4. Construye imagenes candidatas nativas para amd64 y aarch64 usando la etiqueta
   exacta `kimai/kimai2:X.Y.Z`, no `:stable` ni `:2`.
5. En runners desechables, arranca MariaDB 11.4 y la app, comprueba el login y
   el administrador, escribe marcas de prueba en la base de datos y en /data,
   recrea el contenedor de Kimai y verifica que ambas marcas sobreviven.
6. Publica la imagen multi-arquitectura `ghcr.io/estirao/kimai-ha:X.Y.Z` solo
   cuando las pruebas de las dos arquitecturas terminan correctamente.
7. Verifica el manifiesto final, actualiza `kimai/config.yaml`, genera
   `kimai/CHANGELOG.md` y registra `kimai/release.json`.
8. Crea una release `vX.Y.Z` en TU repositorio, con el enlace y las notas de
   la release oficial. Las releases existentes no se duplican ni se borran.
9. Descarga los PNG oficiales y los guarda como `kimai/icon.png` y
   `kimai/logo.png`, con atribucion en `kimai/BRANDING.md`.

Los PNG no estan incluidos como binarios en este ZIP. Se descargan de los
archivos originales `public/touch-icon-192x192.png` y
`public/touch-icon-512x512.png` del repositorio oficial de Kimai durante la
primera publicacion. No se redibujan ni se deforman. El icono es cuadrado, de
192px; el logo usa el simbolo original de 512px. No es un logotipo horizontal.
Home Assistant admite esas dimensiones aunque recomiende otras menores.

Si las imagenes ya existen, el script las conserva. No hace falta una propiedad
`icon:` o `logo:` en config.yaml. Pueden mostrarse tambien en el README con:

```markdown
![Kimai](kimai/logo.png)
```

## Primera ejecucion en GitHub

1. Sube los archivos: Code > Add file > Upload files. Haz commit en main.
2. Ve a Actions > Kimai - detectar y publicar. La subida puede haberlo
   arrancado ya. En otro caso pulsa Run workflow, selecciona main y confirma.
3. Si GitHub pide habilitar Actions para el repositorio, habilitalo.
4. Espera a que detectar, los dos builds y publicar terminen en verde.
5. Comprueba que aparece una release y que existe el paquete kimai-ha.
6. En Packages > kimai-ha > Package settings > Change visibility, comprueba
   que sea Public. Haz lo mismo con amd64-kimai-ha y aarch64-kimai-ha para que
   tambien se puedan descargar directamente las imagenes por arquitectura.

El repositorio publico NO garantiza que un paquete nuevo de GHCR sea publico.
La visibilidad es un ajuste separado y debe comprobarse una vez publicados.

El workflow usa el GITHUB_TOKEN temporal que entrega GitHub. No necesitas crear
un PAT ni guardar tu password de GitHub o de Docker Hub. Declara permisos de
lectura del codigo y, solo en los jobs que los necesitan, escritura del codigo
o de paquetes. Si una politica del repositorio/organizacion impide esos
permisos o los commits a main, el workflow fallara y habra que ajustar esa
politica de forma especifica. No elude protecciones ni fuerza los pushes.

## Cadencia y actualizaciones manuales

Se programa una consulta diaria a las 05:23 UTC y tambien permite ejecucion
manual. Los cron de GitHub pueden retrasarse. Debe estar en la rama default
`main`. Si tu rama por defecto tiene otro nombre, adapta el workflow antes.

El job keepalive hace un commit vacio tecnico SOLO si no hay que publicar y
han pasado al menos 40 dias desde el ultimo commit. Asi se mantiene actividad
en el repositorio frente al limite de inactividad de los cron publicos.

Todo ocurre en GitHub. Ningun script accede a tu IP, a Home Assistant ni a tu
MariaDB de produccion. Las pruebas usan contrasenas aleatorias y bases vacias
creadas y destruidas dentro de los runners de GitHub.

Home Assistant SOLO ofrecera estas actualizaciones a la app instalada desde
este repositorio. Tu instalacion actual `local_kimai` es distinta. Mantener
apagadas las actualizaciones automaticas en la app del repositorio conserva
la decision de instalar o no cada version en Home Assistant. Comprueba ese
ajuste de nuevo al migrar: no asumas que se hereda de la app local.

No desinstales la app local ni arranques simultaneamente otra version sobre la
misma base de datos. La migracion es un paso posterior, con copia de Kimai y
MariaDB y conservando APP_SECRET, datos y plugins.

## Comportamiento ante errores

- Si falta la nueva etiqueta Docker, no compila o no supera la prueba de
  arranque, no se modifica la version que Home Assistant ofrece.
- Se dejan imagenes candidatas de CI en GHCR; no son las que usa la app.
- Si la creacion de la release falla despues de publicar el commit, la proxima
  ejecucion reintenta crearla. release.json evita reconstruir una imagen que
  ya se anuncio. No borres ese archivo mientras recuperas una publicacion.
- Si main cambia durante una compilacion, la publicacion se detiene para no
  mezclar versiones del codigo. Ejecuta de nuevo sobre main.
- Un error al obtener el PNG oficial se resuelve aportando manualmente los
  dos PNG en kimai/ o corrigiendo la ruta; no se guarda una pagina HTML como PNG.
- Un error 403 al publicar requiere revisar los permisos del repositorio y la
  vinculacion del paquete con este repositorio, no las claves de MariaDB.

## Limites que conviene conocer

Quitar el filtro de 2.x NO garantiza compatibilidad con un futuro Kimai 3.x.
Si Kimai cambia el nombre del repositorio Docker `kimai/kimai2`, el sistema
base, el entrypoint, las rutas persistentes o los requisitos de base de datos,
habra que adaptar el Dockerfile, el run.sh o la prueba. Eso no es un bloqueo
por numero de version: evita anunciar una imagen que no arranca.

La prueba es un smoke test en Docker con una MariaDB vacia, no una validacion
completa de Home Assistant OS/AppArmor, de una migracion de tu base actual ni
de tus plugins. Revisa las notas y haz copia conjunta de Kimai y MariaDB antes
de instalar una actualizacion. Volver solo a una imagen vieja no revierte una
migracion de base de datos.

Este flujo sigue las releases de Kimai. No republica una version ya publicada
solo porque hayas cambiado run.sh o el Dockerfile. Las correcciones propias
del empaquetado para una misma version de Kimai necesitan una revision propia
de la app; no conviene sobrescribir imagenes que HA ya ha instalado.

Las imagenes se publican sin firma Cosign en esta primera configuracion.

## Validacion realizada al preparar este paquete

- 19 pruebas unitarias offline del detector, versionado, reintentos,
  sustitucion de config, notas de cambios y manifiesto multi-arquitectura.
- Comprobacion de sintaxis de Bash y Python.
- Parseo y comprobacion de la estructura YAML del workflow.
- NO se ha ejecutado un build Docker ni una publicacion real en GitHub desde
  este entorno. La primera ejecucion en Actions es la comprobacion real.

## Documentacion de referencia

- Publicar apps e imagenes multi-arquitectura:
  https://developers.home-assistant.io/docs/apps/publishing/
- Formato de icono, logo y changelog:
  https://developers.home-assistant.io/docs/apps/presentation/
- Acciones oficiales del builder:
  https://github.com/home-assistant/builder
- Etiquetas y variables de la imagen oficial de Kimai:
  https://www.kimai.org/documentation/docker.html
- API de releases de GitHub:
  https://docs.github.com/en/rest/releases/releases
- GITHUB_TOKEN y visibilidad de GHCR:
  https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- Disparadores y limites de cron:
  https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Recursos graficos oficiales:
  https://github.com/kimai/kimai/tree/main/public

# Kimai para Home Assistant OS

Repositorio comunitario de una aplicación de Kimai para Home Assistant OS.
Usa MariaDB y publica imágenes preconstruidas para **amd64** y **aarch64**.

**Configuración genérica:** no hay una IP de usuario ni credenciales reales.
La zona horaria predeterminada es **Europe/Madrid**.

> Este repositorio es el empaquetado, no la instalación de Kimai ni su base de datos.
> Subir estos archivos a GitHub no modifica una instalación existente.
> La app local y la app del repositorio tienen identificadores distintos.

## Publicar por primera vez

1. Descomprime el ZIP y sube su contenido a la raíz de la rama `main`.
   Deben verse `repository.yaml`, `kimai/`, `scripts/` y `.github/` directamente.
   No subas el ZIP cerrado ni una carpeta adicional que lo envuelva.
2. Incluye también `.gitattributes`, `.gitignore` y `kimai/.dockerignore`.
   GitHub: **Code > Add file > Upload files > Commit changes**.
3. Desactiva workflows antiguos que construyan o publiquen la misma app.
4. Abre **Actions > Kimai - detectar y publicar**. La subida de los archivos de
   código inicia el workflow; también puedes usar **Run workflow**.
5. Espera a que las etapas de detección, construcción/prueba de ambas arquitecturas
   y publicación terminen correctamente.
6. En GitHub Packages, comprueba que **kimai-ha**, **amd64-kimai-ha** y
   **aarch64-kimai-ha** son **Public**. La visibilidad del repositorio no garantiza
   la del paquete. No necesitas crear un token personal.
7. Solo entonces añade este repositorio a la tienda de Home Assistant:

```text
https://github.com/Estirao/home-assistant-kimai
```

Para migrar una app local, lee [MIGRACION.md](MIGRACION.md) antes de iniciar la nueva.
Para una instalación nueva, lee [kimai/DOCS.md](kimai/DOCS.md).

## Actualizaciones, Releases e imágenes

Cada día a las **05:23 UTC** el workflow consulta la última release estable
publicada por `kimai/kimai`. También se puede ejecutar manualmente. No acepta
borradores, betas ni release candidates. **No limita la versión principal**:
una futura 3.x, 4.x o posterior se tratará igual que una 2.x.

Se construye desde una etiqueta exacta `kimai/kimai2:X.Y.Z`, no desde `:2` ni
`:stable`. Si no existe la imagen correspondiente o no supera las pruebas, no
se anuncia la actualización a Home Assistant. Una versión principal nueva puede
exigir adaptar el empaquetado, actualizar MariaDB o revisar plugins.

Las pruebas se ejecutan en runners desechables de GitHub con una MariaDB de
prueba. Comprueban la página de acceso, la creación del administrador y la
persistencia de datos SQL y archivos tras recrear el contenedor de la app.
No conectan a tu Home Assistant ni comprueban la migración de tu base real.

Tras superar las pruebas se publica el manifiesto multi-arquitectura, se
comprueba que tenga amd64 y arm64 y, después, se actualizan `version` en
`kimai/config.yaml`, `kimai/CHANGELOG.md`, el registro `kimai/release.json` y la
release `vX.Y.Z` en la pestaña **Releases**.

El valor `2.67.0` incluido es el punto de partida de este paquete, no una
comprobación de cuál es la última versión en el momento de subirlo. El detector
hace esa consulta real en cada ejecución. No realiza degradaciones automáticas.

**Mantén desactivada la actualización automática de la app en Home Assistant.**
El workflow no cambia ese ajuste ni llama a Home Assistant. `boot: auto` solo
indica que la app arranque con el sistema, no que se actualice sola.

El chequeo programado puede retrasarse por GitHub. Se incluye un commit técnico
vacío tras 40 días sin commits y sin publicaciones pendientes para mantener
actividad; revisa Actions si deja de ejecutarse. Un workflow ya deshabilitado
requiere que lo vuelvas a habilitar.

## Icono y logotipo oficiales

El ZIP contiene el descargador, no copias de los PNG. La primera publicación
correcta añade al repositorio `kimai/icon.png` y `kimai/logo.png`, descargados
sin redibujar desde el repositorio oficial de Kimai. Se valida que sean PNG
cuadrados. Consulta [kimai/BRANDING.md](kimai/BRANDING.md).

No tienes que crear otra imagen ni editar `config.yaml` para el logotipo.
También se puede descargar solo el material gráfico en un ordenador con Python e
Internet mediante `python3 scripts/kimai_release.py branding` y subir los PNG.

## Datos que permanecen fuera de GitHub

Configura en Home Assistant la clave de MariaDB, el administrador inicial, el
`app_secret` y los hosts permitidos. No publiques `options.json`, copias de
seguridad, archivos `.env` ni volcados SQL.

El acceso predeterminado permite los nombres locales `homeassistant.local`,
`localhost` y el loopback. Para entrar por otra IP o dominio, añádelo en la
opción `trusted_hosts` de la app instalada, no en el repositorio público.

## Archivos principales

```text
.github/workflows/kimai-release.yml
.gitattributes
.gitignore
repository.yaml
README.md
MIGRACION.md
COMPROBACIONES.md
LICENSE
kimai/
  config.yaml
  Dockerfile
  .dockerignore
  run.sh
  README.md
  DOCS.md
  CHANGELOG.md
  BRANDING.md
  translations/es.yaml
  translations/en.yaml
scripts/
  kimai_release.py
  test_kimai_release.py
  smoke-test.sh
```

`icon.png`, `logo.png` y `release.json` se generan durante la publicación.

## Reutilizar el repositorio

El workflow calcula el namespace de GHCR a partir del propietario del repositorio
y lo convierte a minúsculas. Para un fork cambia las URL de `repository.yaml`
y `kimai/config.yaml`, su `maintainer` y `image` en `kimai/config.yaml`. No hay
una cuenta personal fijada dentro de los scripts. Este paquete está listo para
publicarse en `Estirao/home-assistant-kimai` sin cambiar esas referencias.

## Mantenimiento del empaquetado

Esta automatización publica nuevas versiones de Kimai; no sobrescribe una imagen
ni una release ya publicada con la misma versión. Cambiar `run.sh` o `Dockerfile`
no vuelve a publicar por sí solo un tag ya existente. No reutilices este ZIP para
pisar el historial o reducir `version` de un repositorio que ya esté más avanzado.
Para publicar correcciones del empaquetado con el mismo Kimai, define primero una
revisión propia y su etiquetado; no borres releases instaladas ni muevas sus tags.

## Fuentes

- [Kimai Docker](https://www.kimai.org/documentation/docker.html)
- [Kimai Docker Compose](https://www.kimai.org/documentation/docker-compose.html)
- [Configuración de apps de Home Assistant](https://developers.home-assistant.io/docs/apps/configuration/)
- [Publicación de apps](https://developers.home-assistant.io/docs/apps/publishing/)
- [Icono y logotipo](https://developers.home-assistant.io/docs/apps/presentation/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases/releases)
- [GitHub: ejecuciones programadas](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Detección de versión SQL en Doctrine](https://www.doctrine-project.org/projects/doctrine-dbal/en/current/reference/configuration.html#automatic-platform-version-detection)

El empaquetado original se distribuye bajo MIT; Kimai y los componentes de sus
imágenes mantienen sus propias licencias. El nombre y los recursos gráficos no
implican que esta app comunitaria sea oficial.

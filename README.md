# Kimai for Home Assistant OS

Contenedor comunitario de **Kimai** preparado para ejecutarse como aplicación de **Home Assistant OS**.

Este repositorio adapta la imagen oficial de Kimai al sistema de aplicaciones de Home Assistant, utiliza una base de datos MariaDB externa y publica imágenes preconstruidas para **amd64** y **aarch64** mediante GitHub Container Registry.

> Este proyecto no forma parte de Kimai ni de Home Assistant. Es un empaquetado comunitario que utiliza la imagen oficial de Kimai como base.

## ¿Qué instala exactamente?

La aplicación no instala una segunda instancia de Home Assistant ni una base de datos dentro del mismo contenedor. La arquitectura es:

```text
Home Assistant OS
│
├── Home Assistant
│
├── MariaDB
│   └── Base de datos: kimai
│
└── Kimai
    ├── Imagen base oficial: kimai/kimai2:<version>
    ├── Interfaz web: puerto 8001/TCP
    ├── Datos persistentes: /data/kimai-data
    └── Plugins persistentes: /data/kimai-plugins
```

El contenedor de este repositorio añade únicamente la capa necesaria para que Kimai pueda configurarse y mantenerse correctamente desde Home Assistant OS.

## Características

- Basado en la **imagen Docker oficial de Kimai**.
- Compatible con **amd64** y **aarch64**.
- Diseñado para **Home Assistant OS / Supervisor**.
- Usa una instancia externa de **MariaDB**; por defecto, la aplicación oficial `core-mariadb` de Home Assistant.
- Mantiene los datos y plugins de Kimai en el almacenamiento persistente de la aplicación.
- Zona horaria predeterminada: **Europe/Madrid**.
- No contiene una IP privada, contraseña ni credencial personal preconfigurada.
- Publica imágenes preconstruidas en **GitHub Container Registry (GHCR)**.
- Comprueba automáticamente si Kimai publica una nueva versión estable.
- No limita las actualizaciones a Kimai 2.x: una futura versión 3.x, 4.x, etc. también puede ser detectada.
- Crea una entrada en **GitHub Releases** por cada versión publicada correctamente.
- Mantiene la instalación automática de actualizaciones separada de la publicación: Home Assistant puede mostrar que existe una actualización sin instalarla automáticamente.

## Cómo funciona el contenedor

La imagen se construye a partir de una versión concreta de Kimai:

```dockerfile
ARG BUILD_VERSION
FROM kimai/kimai2:${BUILD_VERSION}
```

No se utiliza una etiqueta móvil como `latest`, `stable` o `2`. Cada imagen publicada queda asociada a una versión concreta de Kimai.

Al arrancar, `run.sh` lee las opciones guardadas por Home Assistant en:

```text
/data/options.json
```

y las convierte en las variables de entorno que espera Kimai, entre ellas:

```text
DATABASE_URL
APP_SECRET
TRUSTED_HOSTS
ADMINMAIL
ADMINPASS
TIMEZONE
TZ
```

Antes de arrancar Kimai también valida la configuración, prepara la persistencia y configura la zona horaria del sistema y de PHP.

Finalmente ejecuta el `entrypoint.sh` original de la imagen oficial de Kimai. Es decir, el contenedor no sustituye el mecanismo de arranque de Kimai: lo prepara para funcionar correctamente dentro de Home Assistant.

## Base de datos

Kimai necesita una base de datos SQL persistente. Esta aplicación está preparada para conectarse a MariaDB.

La configuración predeterminada espera:

```yaml
database_host: core-mariadb
database_port: 3306
database_name: kimai
database_user: kimai
database_version: auto
```

La contraseña no se almacena en este repositorio. Se introduce desde la configuración de la aplicación en Home Assistant.

`database_version: auto` permite a Doctrine detectar la versión real del servidor MariaDB. También puede especificarse manualmente una versión si fuera necesario para diagnóstico o compatibilidad.

### Ejemplo de configuración de MariaDB

Si ya utilizas MariaDB para otras aplicaciones, conserva las bases de datos y usuarios existentes y añade Kimai. Un ejemplo mínimo sería:

```yaml
databases:
  - kimai

logins:
  - username: kimai
    password: "CAMBIAR_POR_UNA_CLAVE_SEGURA"

rights:
  - username: kimai
    database: kimai
```

## Persistencia

La información principal de Kimai se divide en dos lugares:

### MariaDB

La base de datos contiene, entre otros elementos:

- usuarios;
- clientes;
- proyectos;
- actividades;
- registros horarios;
- configuración almacenada en base de datos.

### Almacenamiento persistente de la aplicación

El contenedor conserva:

```text
/data/kimai-data
/data/kimai-plugins
```

Estas rutas se enlazan respectivamente con:

```text
/opt/kimai/var/data
/opt/kimai/var/plugins
```

De este modo, reconstruir o actualizar el contenedor no debería eliminar los datos persistentes de la aplicación.

> La base de datos MariaDB y los datos persistentes del contenedor son elementos distintos. Para una copia de seguridad completa deben conservarse ambos.

## Acceso web

Kimai se publica mediante HTTP en:

```text
puerto 8001/TCP
```

La interfaz puede abrirse mediante el botón **Abrir interfaz web** de Home Assistant o con el nombre/IP del servidor y el puerto correspondiente.

Ejemplo genérico:

```text
http://homeassistant.local:8001
```

No se incluye una IP concreta en el repositorio.

### `trusted_hosts`

Kimai valida el host utilizado para acceder a la aplicación. La configuración predeterminada es:

```yaml
trusted_hosts: '^(homeassistant\.local|localhost|127\.0\.0\.1)$'
```

Si se accede mediante otra IP, nombre DNS, proxy inverso o Tailscale, ese host debe añadirse en la configuración instalada de Home Assistant.

No debe incluirse el protocolo ni el puerto en `trusted_hosts`.

Ejemplo genérico con un dominio propio:

```yaml
trusted_hosts: '^(homeassistant\.local|kimai\.example\.com|localhost|127\.0\.0\.1)$'
```

Un error HTTP `400` al abrir Kimai puede deberse a que el host utilizado no está autorizado.

## Zona horaria

La configuración predeterminada es:

```yaml
timezone: Europe/Madrid
```

La aplicación aplica esa zona horaria a:

- `TZ`;
- `TIMEZONE`;
- `/etc/localtime`;
- `/etc/timezone`;
- `date.timezone` de PHP.

Se utiliza una zona IANA (`Europe/Madrid`) y no un desplazamiento fijo como `UTC+1` o `UTC+2`, por lo que los cambios estacionales de horario pueden aplicarse correctamente.

Las preferencias horarias de cada usuario dentro de Kimai pueden seguir teniendo su propia configuración.

## Actualizaciones automáticas del repositorio

El repositorio incluye un workflow de GitHub Actions que revisa periódicamente las releases oficiales de Kimai.

```text
Kimai publica una nueva versión estable
                │
                ▼
GitHub Actions detecta la versión
                │
                ▼
Construye amd64 + aarch64
                │
                ▼
Ejecuta comprobaciones de arranque y persistencia
                │
                ▼
Publica imágenes en GHCR
                │
                ▼
Actualiza config.yaml / CHANGELOG / release.json
                │
                ▼
Crea GitHub Release vX.Y.Z
                │
                ▼
Home Assistant puede mostrar la actualización disponible
```

### Sin límite de versión principal

La detección no está limitada a la rama `2.x`.

Si Kimai publica en el futuro:

```text
3.0.0
4.0.0
...
```

el workflow podrá detectarlo igualmente.

Esto **no significa que una versión principal nueva deba instalarse sin revisión**. Puede implicar cambios de requisitos, migraciones de base de datos, incompatibilidades con plugins o cambios en el propio contenedor.

Por ese motivo se recomienda dejar desactivada la actualización automática de la aplicación en Home Assistant y revisar cada nueva versión antes de instalarla.

## GitHub Releases

Cuando una versión supera correctamente el proceso de construcción y pruebas, el repositorio crea una release del tipo:

```text
Kimai X.Y.Z - Home Assistant
Tag: vX.Y.Z
```

También se actualizan:

```text
kimai/config.yaml
kimai/CHANGELOG.md
kimai/release.json
```

La versión anunciada a Home Assistant solo se modifica después de que la imagen correspondiente haya sido preparada correctamente.

## Imágenes publicadas

La imagen principal se publica como:

```text
ghcr.io/estirao/kimai-ha:<version>
```

El manifiesto multi-arquitectura permite que Home Assistant seleccione automáticamente la variante correspondiente al equipo:

```text
amd64
arm64 / aarch64
```

## Icono y logotipo

Home Assistant puede mostrar el icono y el logotipo de la aplicación mediante:

```text
kimai/icon.png
kimai/logo.png
```

El workflow está preparado para obtener los recursos gráficos correspondientes desde el proyecto oficial de Kimai y añadirlos al repositorio durante la publicación.

Consulta:

```text
kimai/BRANDING.md
```

para conocer la procedencia de dichos recursos.

## Instalación en Home Assistant

Una vez exista al menos una imagen publicada correctamente:

1. Abre **Ajustes → Aplicaciones → Tienda de aplicaciones**.
2. Abre el menú de repositorios.
3. Añade:

```text
https://github.com/Estirao/home-assistant-kimai
```

4. Busca **Kimai**.
5. Instala la aplicación.
6. Configura MariaDB, credenciales, `app_secret` y `trusted_hosts`.
7. Inicia Kimai.

Para una instalación detallada consulta:

```text
kimai/DOCS.md
```

Si ya utilizabas una aplicación local de Kimai, consulta primero:

```text
MIGRACION.md
```

## Configuración de la aplicación

Ejemplo genérico:

```yaml
database_host: core-mariadb
database_port: 3306
database_name: kimai
database_user: kimai
database_password: "CONTRASENA_DEL_USUARIO_KIMAI"
database_version: auto
admin_email: "administrador@example.com"
admin_password: "CONTRASENA_INICIAL_DEL_ADMIN"
app_secret: "SECRETO_ALEATORIO_LARGO"
trusted_hosts: '^(homeassistant\.local|localhost|127\.0\.0\.1)$'
timezone: Europe/Madrid
```

Para generar un secreto aleatorio:

```bash
openssl rand -hex 32
```

No publiques credenciales reales, `options.json`, copias SQL o archivos `.env` en GitHub.

## Copias de seguridad

La aplicación utiliza:

```yaml
backup: cold
```

pero una copia de la aplicación Kimai no sustituye una copia de MariaDB.

Para poder recuperar una instalación completa conviene conservar conjuntamente:

```text
1. Aplicación Kimai
2. Base de datos MariaDB
3. /data/kimai-data
4. /data/kimai-plugins
5. app_secret utilizado por la instalación
```

Antes de una actualización importante de Kimai es recomendable crear una copia de seguridad de Kimai y MariaDB.

## Seguridad

- No publiques contraseñas ni secretos en el repositorio.
- No abras directamente el puerto `8001` a Internet sin una capa de protección adecuada.
- Para acceso remoto utiliza preferentemente VPN o un proxy HTTPS correctamente configurado.
- Mantén `trusted_hosts` limitado a los hosts que realmente utilices.
- Conserva `app_secret` al migrar una instalación existente.
- Revisa especialmente las actualizaciones de versión principal antes de instalarlas.

## Estructura del repositorio

```text
home-assistant-kimai/
├── .github/
│   └── workflows/
│       └── kimai-release.yml
├── scripts/
│   ├── kimai_release.py
│   ├── smoke-test.sh
│   └── test_kimai_release.py
├── kimai/
│   ├── config.yaml
│   ├── Dockerfile
│   ├── run.sh
│   ├── DOCS.md
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── BRANDING.md
│   └── translations/
├── repository.yaml
├── MIGRACION.md
├── COMPROBACIONES.md
└── README.md
```

## Archivos principales

**`kimai/config.yaml`**  
Define la aplicación para Home Assistant: versión, arquitecturas, puerto, opciones, imagen de GHCR y comportamiento de arranque.

**`kimai/Dockerfile`**  
Construye la imagen sobre una versión concreta de `kimai/kimai2` y añade las dependencias necesarias para integrarla con Home Assistant.

**`kimai/run.sh`**  
Traduce las opciones de Home Assistant a variables de entorno de Kimai, valida la configuración, prepara la persistencia y ejecuta el entrypoint oficial.

**`.github/workflows/kimai-release.yml`**  
Automatiza la detección, construcción, pruebas y publicación de nuevas versiones.

**`scripts/kimai_release.py`**  
Gestiona la lógica de detección y preparación de releases.

**`scripts/smoke-test.sh`**  
Realiza las comprobaciones básicas del contenedor antes de publicarlo.

## Diagnóstico

Desde Terminal & SSH de Home Assistant pueden consultarse los registros de la aplicación mediante su slug real:

```bash
ha apps logs <slug_de_kimai>
```

Errores frecuentes:

- **HTTP 400** → revisar `trusted_hosts`.
- **Access denied / SQLSTATE** → revisar usuario, contraseña y permisos de MariaDB.
- **Connection refused** → revisar `database_host`, puerto y estado de MariaDB.
- **Kimai no conserva información** → comprobar MariaDB y la persistencia de `/data`.

Una prueba sencilla consiste en crear un cliente o proyecto, reiniciar únicamente Kimai y comprobar que continúa disponible.

## Licencia y marcas

El código específico de este empaquetado se distribuye según la licencia incluida en este repositorio.

Kimai, Home Assistant, sus imágenes Docker, nombres, logotipos y demás componentes mantienen sus respectivas licencias y marcas.

La presencia del nombre o logotipo de Kimai no implica que esta aplicación comunitaria sea una distribución oficial ni que esté mantenida por el proyecto Kimai.

## Enlaces de referencia

- Kimai: https://www.kimai.org/
- Documentación Docker de Kimai: https://www.kimai.org/documentation/docker.html
- Home Assistant Developer Docs: https://developers.home-assistant.io/docs/apps/
- GitHub Container Registry: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

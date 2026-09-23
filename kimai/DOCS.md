# Instalacion y configuracion

## Base de datos

Instala la app MariaDB y crea una base de datos `kimai` y un usuario `kimai`
con permisos sobre esa base. El puerto interno habitual es 3306 y el nombre
interno de la app oficial es `core-mariadb`.

Ejemplo SOLO para una instalacion nueva de MariaDB:

```yaml
databases:
  - kimai
logins:
  - username: kimai
    password: "SUSTITUIR_POR_UNA_CLAVE_LARGA"
rights:
  - username: kimai
    database: kimai
```

Si MariaDB ya contiene otras bases o usuarios, conserva esas entradas y agrega
las de Kimai; no sustituyas toda su configuracion por este ejemplo.

## Opciones de la app instalada

Los valores reales se guardan en Home Assistant, no en GitHub. Mantiene los
nombres de opciones de la app local anterior para facilitar la migracion.

```yaml
database_host: core-mariadb
database_port: 3306
database_name: kimai
database_user: kimai
database_password: "CLAVE_REAL_DEL_USUARIO_KIMAI"
database_version: auto
admin_email: "administrador@example.com"
admin_password: "CLAVE_REAL_DEL_ADMINISTRADOR"
app_secret: "SUSTITUIR_POR_UN_SECRETO_ALEATORIO_DE_64_CARACTERES"
trusted_hosts: '^(homeassistant\.local|localhost|127\.0\.0\.1)$'
timezone: Europe/Madrid
```

`database_version: auto` deja que Doctrine detecte la version SQL al conectar,
sin fijar una version de MariaDB que podria no coincidir con el servidor real.
Tambien admite una version explicita como diagnostico; si ya tienes un valor
explicito correcto puedes conservarlo. No escribe "auto" en la URL SQL.

Para generar un secreto nuevo o una clave larga, ejecuta en un terminal:

```bash
openssl rand -hex 32
```

Usa valores diferentes para los distintos secretos. En una migracion conserva
el `app_secret` original. No vuelvas a generarlo en cada reinicio.

`admin_email` y `admin_password` son para crear el administrador inicial;
no restablecen por si solos la clave de una cuenta que ya existe. Para el correo
saliente habria que configurar SMTP aparte; esta app no lo activa por defecto.

## Acceso y trusted_hosts

El repositorio NO contiene la IP de una instalacion concreta. Por defecto acepta
`homeassistant.local`, `localhost` y el loopback. Desde otro equipo, `localhost`
se refiere a ese equipo, no al servidor Home Assistant.

Cuando `homeassistant.local` resuelva al servidor en tu red, abre:

```text
http://homeassistant.local:8001
```

Si utilizas una IP, abre `http://IP_DE_HOME_ASSISTANT:8001` y anade esa IP al
campo `trusted_hosts` en la app instalada. No la publiques en GitHub. El campo
admite una expresion regular: escapa cada punto con una barra invertida y separa
alternativas con `|`. No incluyas protocolo, puerto, ruta ni barra final.

Ejemplo generico con un dominio, no con una IP de usuario:

```yaml
trusted_hosts: '^(homeassistant\.local|kimai\.example\.com|localhost|127\.0\.0\.1)$'
```

`kimai.example.com` es solo un ejemplo: no funciona sin un DNS real que apunte al
servidor. En el campo de texto de Home Assistant escribe una sola barra `\`
antes de cada punto. En YAML con comillas simples tambien se escribe una sola.
Si usas comillas dobles de YAML, cada barra debe escaparse como `\\`.

Tras cambiar hosts, guarda y reinicia la app. Un HTTP 400 puede ser un host no
permitido; revisa el registro en vez de dejar `.*` como configuracion permanente.

Esta app usa HTTP en el puerto 8001 y no configura Ingress ni HTTPS. No abras
este puerto directamente a Internet. Para acceso remoto utiliza una VPN o un
proxy HTTPS configurado y anade el host utilizado a `trusted_hosts`.

## Zona horaria

`Europe/Madrid` se aplica a TZ/TIMEZONE, a /etc/localtime y al ajuste date.timezone
de PHP. No se usa un desplazamiento fijo como UTC+2. Revisa tambien la zona
horaria en el perfil de usuario de Kimai: sus preferencias son independientes
del reloj del contenedor.

## Persistencia y copias de seguridad

- La base SQL esta en la app MariaDB, no dentro de esta imagen.
- Los archivos de Kimai se conservan en `/data/kimai-data`.
- Los plugins se conservan en `/data/kimai-plugins`.

`/data` es el volumen privado persistente de ESTA app. No es el `/data` de
Terminal & SSH ni se comparte automaticamente con una app local de otro slug.
No cambies esas rutas para simular una migracion.

`backup: cold` detiene esta app para su copia. Una copia solo de Kimai NO incluye
por arte de magia la base SQL de MariaDB. Haz una copia que incluya AMBAS apps;
para una copia coherente, deja de escribir en Kimai mientras se realiza.
Guarda el archivo de copia fuera del propio equipo y prueba una restauracion.

## Actualizar

Deja la actualizacion automatica de la app DESACTIVADA en Home Assistant. Que
GitHub publique una imagen no instala nada en tu equipo. Revisa el changelog,
los requisitos de MariaDB y los plugins, haz una copia conjunta y actualiza
manualmente. Volver a una imagen antigua no revierte migraciones de SQL.

No confundas `boot: auto` (arranque con el sistema) con actualizar automaticamente.

## Diagnostico

Mira los registros de Kimai y MariaDB. No compartas contrasenas ni options.json.
Desde Terminal & SSH, `ha apps logs SLUG_REAL` muestra el registro de la app.
El slug de la app de repositorio no es `local_kimai`.

Crea un cliente y un proyecto de prueba, reinicia solo Kimai y comprueba que se
conservan. Ver la pantalla de acceso, por si sola, no prueba toda la persistencia
ni que una copia de seguridad sea restaurable.

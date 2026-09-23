# Kimai for Home Assistant

This repository provides **Kimai** packaged as a custom application for **Home Assistant OS**.

[Kimai](https://www.kimai.org/) is an open-source time-tracking application designed for recording working hours, projects, customers, activities, users, and related time-management data.

This package is intended for users who want to run Kimai directly from Home Assistant OS and manage it alongside the rest of their Home Assistant applications.

## Requirements

Before installing this application, you need:

- **Home Assistant OS** with Supervisor / Apps support.
- **MariaDB** installed and running in Home Assistant.
- A dedicated MariaDB database for Kimai.
- A dedicated MariaDB user with permissions on the Kimai database.
- A free TCP port for the Kimai web interface. The default configuration uses **port 8001**.
- A supported system architecture:
  - `amd64`
  - `aarch64`

## MariaDB

Kimai requires a database server.

The recommended setup is the official **MariaDB Home Assistant app**, using a dedicated database and user for Kimai.

Example:

```yaml
databases:
  - kimai

logins:
  - username: kimai
    password: YOUR_SECURE_PASSWORD

rights:
  - username: kimai
    database: kimai
```

The Kimai application must then be configured with the same database name, username, and password.

The default internal MariaDB hostname used by Home Assistant is:

```text
core-mariadb
```

## Application configuration

After installation, configure at least:

- MariaDB host
- MariaDB port
- Database name
- Database username
- Database password
- Kimai administrator email
- Kimai administrator password
- Application secret
- Trusted hosts
- Time zone

## Access

By default, Kimai is exposed through:

```text
http://HOME_ASSISTANT_IP:8001
```

The hostname or IP address used to access Kimai must be included in the application's `trusted_hosts` configuration.

## Supported platforms

This package is prepared for:

- Home Assistant OS
- `amd64`
- `aarch64`

It is not intended to replace Kimai's official Docker or Docker Compose installation methods on a standard Linux server.

## Data

Kimai stores its application data in MariaDB.

If plugins or additional Kimai files are used, they may also require persistent application storage.

Regular Home Assistant backups including **MariaDB** are strongly recommended.

## Updates

Application updates are provided through the Home Assistant App Store when a newer packaged Kimai version is available.

Automatic updates can be disabled in Home Assistant so that each Kimai update can be reviewed before installation.

## Project status

This is a community packaging of Kimai for Home Assistant OS.

It is not an official project of either:

- Kimai
- Home Assistant

For information about Kimai itself, visit:

https://www.kimai.org/

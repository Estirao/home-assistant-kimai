# Changelog

## 2.67.0

Kimai **2.67.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.67.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.67.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

- Use timeout in network call, fixes Doctor screen in airgapped environments (#6172)
- Do not hijack the export form for submitting the actual export request, use JS for it (#6172)
- Fix broken redirect on missing permission `edit_team` after using `create_team` (#6172)
- Remove legacy code and deprecate form option (#6172)
- Fix NelmioApiDocBundle warning (#6172)
- Translations update from Hosted Weblate (#6163)
- API: validate recent activity collection limit (#6171)
- Use only translated locales for routes and cache warming (#6148)

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: @kevinpapst, @Roshan931, Amir, @chello-dev, @flytothehighest, @IepIweidieng, Jonathan Carvalho, @oersen, Posemartonis, @ramuroN, @sira3002, @Victoria-hogo, @doanmanhducz and @vintagezero

Las entradas de versiones publicadas se generan automaticamente tras construir y
probar las imagenes. Este archivo inicial no certifica ninguna compilacion.

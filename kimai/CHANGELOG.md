# Changelog

## 2.68.0

Kimai **2.68.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.68.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.68.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Features

- Dropdowns: visible label length increased to 180 char + scroll to selected element on open (#6222)
- Reports: sticky first column in horizontal tables (#6216)
- Better duration input handling on all duration fields (#6210)
- Shorter duration entry: Interpret ints \< 10 as hours and >= 10 as minutes (#6146)
- User locale: default system setting + format examples in dropdown (#6186)
- API: added endpoint to update invoice (#6184)
- User profile: move "copy to clipboard" button to the left (#6184)
- Customer listing: added optional column to show first the line 1 of the address (#6184)
- Weekly-Hours: button to filter timesheets in "All times" view by the selected user and date-range (#6184)
- Translations update from Hosted Weblate (#6190)

**Timesheet Batch-Update**

- Show form error inline instead of flashing it (#6184)
- Show amount of timesheets  (#6184)
- Validate each timesheet during update (#6184)
- Support the optional `break` field (#6184)

#### Bugfixes

- SAML/LDAP - fix invalid Avatar prevents login (#6223)
- Fix URLs with untranslated locales using subregions (broken user profiles) (#6184)
- API: invoice payment date is a date, not a date-time (BC) (#6184)

#### Security

- Timesheet batch-update: throw if timesheet may not be edited, instead of skipping it (#6184)
- Check team access is possible before checking `*_team_x` and `*_teamlead_x` permissions (#6184)
- Check that the user can view the requested team via API (#6184)
- Validate team access on batch-update form for project and activity (#6184) - thanks Humbertosp
- Unify API and UI checks for the timesheet PATCH action (#6184) - thanks devzephyr
- Improve 2FA auth on remember-me accounts (#6184) - thanks AzureADTrent
- Bind `password-reset` and `system-account` flags to "roles" permission (#6184) - thanks AzureADTrent
- Improve wizard route detection to prevent skipped wizards (#6184) - thanks rach1tarora 
- Remove Docker entrypoint debug tracing - thanks AlpetGexha Xylakant
- Disable password reset if `TRUSTED_HOSTS` is not configured (#6226)

#### Maintenance

- API: preload team members users and preferences to avoid N+1 (#6189)
- Dispatch event on invoice status change (#6184)
- Simplify adding translated API forms via form extension and interface (#6184)
- Cleanup swiss translations (#6184)
- Clarify we do NOT accept raw AI output in security reports (#6184)
- Clarify permission check as code comment to prevent further invalid security reports (#6184)

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: Arslan-TR, hacklschorsch, kevinpapst, AgenteGabrielofc, aspopovic, Bartosz Sobótkowski, flytothehighest, mapi68, milotype and stysus

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

Involved in this release: kevinpapst, Roshan931, Amir, chello-dev, flytothehighest, IepIweidieng, Jonathan Carvalho, oersen, Posemartonis, ramuroN, sira3002, Victoria-hogo, doanmanhducz and vintagezero

Las entradas de versiones publicadas se generan automaticamente tras construir y
probar las imagenes. Este archivo inicial no certifica ninguna compilacion.

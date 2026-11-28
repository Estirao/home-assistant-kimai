# Changelog

## 2.74.0

Kimai **2.74.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.74.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.74.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Changes

- API pagination opt-in via parameter (#6363) - thanks jonas-mayer19
- Allow to load work-contract statistics for many users at once (#6361)
- Renamed activity/project/customer permission sections for clarity [see docs](https://www.kimai.org/documentation/permissions.html#permissions) (#6360)
- Hidden customers can now be pre-selected through filter (#6340)
- Make long page-action dropdowns scrollable (#6360)
- Fix autocomplete on login forms (#6360) ([#274](https://github.com/kevinpapst/TablerBundle/issues/274))

#### 🚨 Security

- Bump dependencies 
- Improve pre-selected item handling in toolbar forms (#6359) - thanks dragomir-am and joostgrunwald

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst and jonas-mayer19

## 2.73.0

Kimai **2.73.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.73.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.73.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Changes

- Remove financial year setting, fix broken yearly reports (#6344)
- Invoice: do not show footnote number if tax row was hidden (#6335)
- Throw exception if LDAP is activated but dependency not installed (#6332)
- Fix decimal duration rounding (#6254) - thanks shu-chen-dot-ca
- Bump `phpoffice/phpspreadsheet` to v5 (#6335)
- Translations update from Hosted Weblate (#6328)
- Prevent managing the profiles of higher privileged users (#6350) - thanks HusseinTahaSEC 

#### 🚨 Security

- Do not include user-entity fields in supervisor API subresource (#6347) - thanks kats1123 
- Prevent password login for SAML accounts (#6334) - thanks mrhackcz

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst, AlaxLima, flytothehighest, Massimo Pissarello, Peter Törnstrand and Webcapitalos Adminos

## 2.72.1

Kimai **2.72.1** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.72.1`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.72.1).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

A new release to trigger new Docker images, after the latest CVEs were patched and the base images updated.

## 2.72.0

Kimai **2.72.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.72.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.72.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Features & Maintenance

- Bump Docker to PHP 8.5, use custom ICU data to fix timezone issues in some countries (#6318)
- Search invoice history by invoice number (#6287) - thanks Deniiz23 
- Highlight unpaid invoices in listings
- Run the search on Enter instead of saving the filter as default (invoice & export screen) (#6291) - thanks dgesteves 
- Run `pnpm lint` during CI
- Updated translations (#6292) (#6306)
- Fix twig deprecations: missing default parameter in macros
- Improved invoice overdue calculation (internal API bug, no visible changes)
- Bumped frontend and composer packages

#### Bugfixes

- Keep the calendar month in the URL on reload (#6324) - thanks shu-chen-dot-ca 
- Use correct TTL settings for "password reset" links
- Reduce default TTL for "password reset" links to 0.5h
- Use consistent currency aware monetary rounding half-up, mainly for invoices (#6317)
- Memory safe export preview (#6295)
- Do not fail on unpersisted entities in rate calculation (mass import via internal API)

#### 🚨 Security

- Disable login route if SAML is active and user disabled form login (#6311) - thanks mrtxmrtx
- Validate custom-field values submitted via API (#6301) - thanks wleeaf and manus-pi
- Fix locale route matching in global firewall - thanks petertornstrand 
- Harden twig security policy - thanks manus-pi

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Also involved in this release: kevinpapst, weblate, Andrei Stepanov, aspopovic, Deniiz23, dgesteves, Gabriel, Phil, testecelular and Watchman89

## 2.71.0

Kimai **2.71.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.71.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.71.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Changes

- Remove API password from user profile screen (#6277)
- Deactivate API passwords (#6267) - thanks haxxordan

#### Bugfixes

- Check if API is allowed to set begin (#6275) - thanks Deniiz23
- Use edit permission to check if times can be set via API (#6276) - thanks Deniiz23

#### Maintenance

- Convert user roles from deprecated Types::ARRAY to Types::JSON (#6278)
- Translations update from Hosted Weblate (#6258)
- Dependency updates (#6272)

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst, haxxordan, Deniiz23, Olaf Nielsen and yurisatori0312

## 2.70.2

Kimai **2.70.2** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.70.2`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.70.2).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

* Rebuild docker images for ARM - thanks dasrecht

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst

## 2.70.0

Kimai **2.70.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.70.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.70.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Features

- Password strength configuration (#6242)
- CSS classes for customization (working contract screen) (#6240)
- Translations update from Hosted Weblate (#6235) (#6253)

#### 🚨 Security

- Prevent internal preferences from being updated via API - thanks sharma19d (#6240)
- Make sure that remembered users cannot skip the password-change wizard - thanks sharma19d (#6240)
- Update security-signature on password-reset and end all active sessions - thanks Tan-JunWei (#6240)
- Added EnvVarProcessor to parse TRUSTED\_HOSTS - thanks dylanzonix (#6246)
- Only the logged-in user can activate 2fa - thanks AzureADTrent (#6240)

You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst, AgenteGabrielofc, alhyei6si, Anastasija FG, Andrei Stepanov, arifpedia, aspopovic, Michal Várady, oersen,Ph1l0s64, Watchman89

## 2.69.0

Kimai **2.69.0** packaged for Home Assistant OS.

Image: `ghcr.io/estirao/kimai-ha:2.69.0`. Architectures: `amd64` and `aarch64`.

[Official Kimai release](https://github.com/kimai/kimai/releases/tag/2.69.0).

Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.

Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.

Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. This is not a test of migration from your existing database or of installed plugins.

#### Official Kimai release notes

**Compatible with PHP 8.2 to 8.5**

#### Features

- Reset user security signature on change of relevant fields (#6230)
- Allow to switch LDAP/SAML accounts to internal (#6229)
- New choice form type that supports re-ordering and that keeps the saved column order when editing (#6228)
  - Export template column
  - Activity dropdown title pattern
  - Project dropdown title pattern
  - Customer dropdown title pattern
- Login links should always use 2FA (#6228)
- Translations update from Hosted Weblate (#6225)

#### Bugfixes 

- The "Project details" report was not visible for teamleads (#6228)
- Missing "Project details" route did not highlight report menu (#6228)
- Use `DEFAULT_URI` in login-link command to fix "Untrusted Host" (#6228)


You can read more about all security reports [here](https://www.kimai.org/documentation/bughunter.html#published-vulnerabilities) or grab this [RSS feed](https://www.kimai.org/security.xml) to get notified about new published advisories.

Involved in this release: kevinpapst, AgenteGabrielofc, oersen, persianboy, yarons and z0ranf

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

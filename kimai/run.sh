#!/usr/bin/env bash
# Home Assistant options -> official Kimai environment. Never print secrets.
set -Eeuo pipefail
set +x
umask 022
CONFIG="/data/options.json"

fail() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }
[[ -r "$CONFIG" ]] || fail "Falta /data/options.json. Inicia esta imagen como app de Home Assistant."
jq -e 'type == "object"' "$CONFIG" >/dev/null || fail "options.json no es un objeto JSON valido."
option() { jq -er --arg key "$1" '.[$key] | select(. != null) | tostring' "$CONFIG"; }

DB_HOST="$(option database_host)"
DB_PORT="$(option database_port)"
DB_NAME="$(option database_name)"
DB_USER="$(option database_user)"
DB_PASS="$(option database_password)"
DB_VERSION="$(jq -r '.database_version // "auto"' "$CONFIG")"
ADMIN_EMAIL="$(option admin_email)"
ADMIN_PASS="$(option admin_password)"
KIMAI_SECRET="$(option app_secret)"
KIMAI_HOSTS="$(option trusted_hosts)"
TZ_KIMAI="$(option timezone)"

[[ "$DB_HOST" =~ ^[A-Za-z0-9_.-]+$ ]] || fail "database_host debe ser una IP IPv4 o un nombre DNS, sin protocolo ni puerto."
[[ "$DB_PORT" =~ ^[0-9]{1,5}$ ]] || fail "database_port no es un puerto valido."
(( 10#$DB_PORT >= 1 && 10#$DB_PORT <= 65535 )) || fail "database_port fuera de rango."
[[ -n "$DB_NAME" && -n "$DB_USER" ]] || fail "Falta el nombre de base de datos o usuario."
[[ -n "$DB_PASS" && "$DB_PASS" != CHANGE_ME* ]] || fail "Configura database_password en Home Assistant."
[[ -n "$ADMIN_PASS" && "$ADMIN_PASS" != CHANGE_ME* ]] || fail "Configura admin_password en Home Assistant."
[[ ${#KIMAI_SECRET} -ge 32 && "$KIMAI_SECRET" != CHANGE_ME* ]] || fail "Configura app_secret: minimo 32 caracteres aleatorios."
[[ -n "$KIMAI_HOSTS" ]] || fail "Configura trusted_hosts con el host usado para acceder."
[[ "$KIMAI_HOSTS" != *"://"* ]] || fail "trusted_hosts no debe incluir http://, https:// ni el puerto."
[[ "$TZ_KIMAI" =~ ^[A-Za-z0-9_+./-]+$ && "$TZ_KIMAI" != *".."* && -f "/usr/share/zoneinfo/$TZ_KIMAI" ]] || fail "Zona horaria desconocida. Ejemplo: Europe/Madrid."

urlencode() { php -r 'echo rawurlencode($argv[1]);' "$1"; }
DB_USER_ENC="$(urlencode "$DB_USER")"
DB_PASS_ENC="$(urlencode "$DB_PASS")"
DB_NAME_ENC="$(urlencode "$DB_NAME")"
export DATABASE_URL="mysql://${DB_USER_ENC}:${DB_PASS_ENC}@${DB_HOST}:${DB_PORT}/${DB_NAME_ENC}?charset=utf8mb4"
# Without serverVersion Doctrine detects the actual server version itself.
if [[ -n "$DB_VERSION" && "$DB_VERSION" != "auto" ]]; then
  DATABASE_URL+="&serverVersion=$(urlencode "$DB_VERSION")"
fi
export APP_ENV="prod"
export APP_SECRET="$KIMAI_SECRET"
export TRUSTED_HOSTS="$KIMAI_HOSTS"
export ADMINMAIL="$ADMIN_EMAIL"
export ADMINPASS="$ADMIN_PASS"
export MAILER_FROM="$ADMIN_EMAIL"
export TIMEZONE="$TZ_KIMAI"
export TZ="$TZ_KIMAI"

# Keep the established /data locations compatible with the local app.
# Seed missing files without overwriting already-persisted user data.
link_persistent() {
  local source="$1" target="$2"
  mkdir -p "$target"
  if [[ -L "$source" ]]; then
    [[ "$(readlink "$source")" == "$target" ]] || fail "Enlace de datos inesperado: $source. Revisar antes de arrancar."
    return
  fi
  if [[ -d "$source" ]]; then
    if [[ -z "$(find "$target" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
      cp -a "$source/." "$target/"
    fi
    rm -rf -- "$source"
  elif [[ -e "$source" ]]; then
    fail "Se esperaba un directorio en $source."
  fi
  ln -s "$target" "$source"
}
link_persistent /opt/kimai/var/data /data/kimai-data
link_persistent /opt/kimai/var/plugins /data/kimai-plugins
chown -R www-data:www-data /data/kimai-data /data/kimai-plugins

ln -snf "/usr/share/zoneinfo/$TZ_KIMAI" /etc/localtime
printf '%s\n' "$TZ_KIMAI" > /etc/timezone
# PHP and the OS use the same named timezone, not a fixed UTC offset.
printf 'date.timezone = "%s"\n' "$TZ_KIMAI" > /usr/local/etc/php/conf.d/99-home-assistant-timezone.ini
chmod 644 /usr/local/etc/php/conf.d/99-home-assistant-timezone.ini

printf 'Iniciando Kimai. MariaDB: %s:%s; base: %s; zona: %s\n' "$DB_HOST" "$DB_PORT" "$DB_NAME" "$TZ_KIMAI"
exec /entrypoint.sh

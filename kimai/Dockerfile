# CI supplies one concrete stable release; future major versions are allowed.
ARG BUILD_VERSION
FROM kimai/kimai2:${BUILD_VERSION}

ARG BUILD_VERSION
ARG BUILD_ARCH
USER root

LABEL io.hass.type="app" \
      io.hass.version="${BUILD_VERSION}" \
      io.hass.arch="${BUILD_ARCH}"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends jq tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && test -f /entrypoint.sh \
    && sed -i -e '1s/ -x$//' -e 's/set -x/set +x/g' /entrypoint.sh

# Do not trace the upstream bootstrap: command traces can expose DB/admin secrets.
COPY run.sh /run-ha.sh
RUN chmod 755 /run-ha.sh
CMD ["/run-ha.sh"]

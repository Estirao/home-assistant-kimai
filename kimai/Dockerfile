# The workflow supplies a concrete stable Kimai version, including future majors.
ARG BUILD_VERSION
FROM kimai/kimai2:${BUILD_VERSION}

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

# Keep the run.sh already tested on Home Assistant.
COPY run.sh /run-ha.sh
RUN chmod 755 /run-ha.sh

CMD ["/run-ha.sh"]

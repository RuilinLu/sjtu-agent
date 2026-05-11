FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl iproute2 iptables strongswan strongswan-pki strongswan-swanctl \
       libcharon-extauth-plugins libstrongswan-extra-plugins \
       libcharon-extra-plugins libstrongswan-standard-plugins \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

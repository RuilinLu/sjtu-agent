#!/bin/sh
set -eu

: "${SJTU_AGENT_CONFIGURE_DNS:=1}"
: "${SJTU_AGENT_DNS_SERVERS:=202.120.2.101 202.112.26.40 223.5.5.5}"

if [ "${SJTU_AGENT_CONFIGURE_DNS}" = "1" ]; then
    : > /etc/resolv.conf
    for ns in ${SJTU_AGENT_DNS_SERVERS}; do
        echo "nameserver ${ns}" >> /etc/resolv.conf
    done
    echo "options timeout:2 attempts:2" >> /etc/resolv.conf
fi

exec "$@"

#!/usr/bin/env sh
set -eu

: "${SJTU_VPN_SERVER:=stuv4.vpn.sjtu.edu.cn}"
: "${SJTU_VPN_ID:=@stu.vpn.sjtu.edu.cn}"
: "${SJTU_VPN_RIGHTSUBNET:=0.0.0.0/0}"
: "${SJTU_VPN_LEFTAUTH:=eap-peap}"
: "${SJTU_VPN_RIGHTAUTH:=pubkey}"
: "${SJTU_VPN_USER:?SJTU_VPN_USER is required}"
: "${SJTU_VPN_PASSWORD:?SJTU_VPN_PASSWORD is required}"

mkdir -p /etc/ipsec.d/cacerts
if [ -f /etc/ssl/certs/ISRG_Root_X1.pem ]; then
    cp /etc/ssl/certs/ISRG_Root_X1.pem /etc/ipsec.d/cacerts/ISRG_Root_X1.pem
fi

cat >/etc/ipsec.conf <<EOF
config setup
    uniqueids=no
    charondebug="ike 1, knl 1, cfg 1"

conn sjtu-student
    keyexchange=ikev2
    auto=start
    left=%defaultroute
    leftsourceip=%config
    leftid=${SJTU_VPN_USER}
    leftauth=${SJTU_VPN_LEFTAUTH}
    eap_identity=${SJTU_VPN_USER}
    right=${SJTU_VPN_SERVER}
    rightid=${SJTU_VPN_ID}
    rightauth=${SJTU_VPN_RIGHTAUTH}
    rightsubnet=${SJTU_VPN_RIGHTSUBNET}
    fragmentation=yes
    dpdaction=restart
    dpddelay=30s
    dpdtimeout=150s
EOF

cat >/etc/ipsec.secrets <<EOF
${SJTU_VPN_USER} : EAP "${SJTU_VPN_PASSWORD}"
EOF
chmod 600 /etc/ipsec.secrets

echo "[sjtu-vpn] starting strongSwan for ${SJTU_VPN_SERVER}"
exec ipsec start --nofork

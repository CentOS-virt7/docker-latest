#!/bin/sh

LOGROTATE=true
[ -f /etc/sysconfig/docker-latest ] && source /etc/sysconfig/docker-latest

if [ $LOGROTATE == true ]; then
    for id in $(docker-latest ps -q); do
        exec $(docker-latest exec $id logrotate -s /var/log/logstatus /etc/logrotate.conf > /dev/null 2>&1)
    done
fi
exit 0

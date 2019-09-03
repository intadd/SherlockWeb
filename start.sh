celery multi start worker1 -A sherlock --pidfile="/var/run/celery/%n.pid" --logfile="/var/log/celery/%n%I.log" --autoscale=10,5

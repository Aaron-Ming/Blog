#!/bin/bash
#init system service script

if [ $(whoami) != "root" ]; then
    echo "You don't have permission to run this script!"
    exit 1
fi

BASE=$(cd `dirname $0` ; pwd)
ProcessName=$(grep "ProcessName" ${BASE}/../BLOG/Tools/config.py | grep -v ^$ | awk -F "ProcessName = " '{print $2}' | awk -F \" '{print $2}' | grep -v ^$)
ApplicationHome=$(grep "ApplicationHome" ${BASE}/../BLOG/Tools/config.py | grep -v ^$ | awk -F "ApplicationHome = " '{print $2}' | awk -F \" '{print $2}' | grep -v ^$)
initd="/etc/init.d/blog"
[ -z $ProcessName ] && ProcessName="blog"

cat > $initd << 'EOF'
#!/bin/bash
# chkconfig: 29 2345 155
# description: Daemon for ProcessName
# Source function library.

exec="/usr/bin/python"

#You can define file with config.py.
app_name="ProcessName"
basedir="ApplicationHome"

#You can define file, but need permission.
pidfile="/tmp/${app_name}.pid"
logfile="${basedir}/sys.log"

case $1 in
start)
    if [ -f $pidfile ]; then
        echo "$pidfile still exists..." ; exit 1
    else
        echo "Starting Application ${app_name}......"
        $exec ${basedir}/BLOG/Product_start.py &>> $logfile &
        pid=$!
        echo $pid > $pidfile
        PS=$(ps -A | awk '{print $1}' | grep -v PID | grep $pid | wc -l)&> /dev/null
        if [ $PS != "1" ]; then
            kill $(cat $pidfile) && rm -f $pidfile
            echo "Start Error"
        fi
    fi
    ;;

stop)
    echo $"Stopping Application ${app_name}!"
    kill -9 `cat $pidfile`
    retval=$?
    [ $retval -eq 0 ] && rm -f $pidfile
    ;;

restart)
    $0 stop
    $0 start
    ;;

*)
    echo "Usage: $0 {start|stop|restart}"
    exit 2
    ;;
esac

exit $?
EOF

sudo sed -i "s/ProcessName/${ProcessName}/" $initd
sudo sed -i "s#ApplicationHome#${ApplicationHome}#" $initd
sudo chmod +x $initd

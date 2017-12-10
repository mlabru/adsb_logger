#!/bin/bash

# need to wait past boot so everything is done
sleep 2

# data do sistema
DATE=`date '+%Y%m%d.%H%M'`

# nome do computador
HOST=`hostname`

# diretório de execução
EXEC_DIR=/home/mlabru/Public/wrk.adsb/adsb_logger

# executa a aplicação (-OO)
# /usr/bin/env python -OO $EXEC_DIR/gps_serial.py "$@" 2> $EXEC_DIR/logs/gps_serial.$HOST.$DATE.log 1>&2 &

# executa a aplicação (-OO)
dump1090 --raw | /usr/bin/env python $EXEC_DIR/adsb_logger.py --display "$@" 2> $EXEC_DIR/logs/adsb_logger.$HOST.$DATE.log 1>&2 & 

exit 0

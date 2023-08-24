#!/bin/sh

# stop circus managed mxcube and run new mxcube in this terminal
circusctl stop mxcube
/app/web/mxcube3-server --repository /app/conf/MicroMAX --static-folder /app/web/ui/build

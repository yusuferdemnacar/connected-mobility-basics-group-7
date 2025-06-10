#! /bin/sh
java -Xmx1024M -cp target:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim $*

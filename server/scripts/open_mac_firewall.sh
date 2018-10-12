#!/bin/sh
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Library/PrivilegedHelperTools/com.docker.vmnetd;
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Library/PrivilegedHelperTools/com.docker.vmnetd;

if ACCEPT_EULA=Y apt-get install -f -y msodbcsql17 ; then
   echo "OK"
else
   echo "Error"
   rm /var/lib/dpkg/info/msodbcsql17.postinst
   ACCEPT_EULA=Y apt-get install -f -y msodbcsql17
fi
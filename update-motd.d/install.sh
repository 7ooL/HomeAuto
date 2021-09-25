chmod -x /etc/update-motd.d/00-header
chmod -x /etc/update-motd.d/10-help-text
chmod -x /etc/update-motd.d/50-landscape-sysinfo
chmod -x /etc/update-motd.d/50-motd-news
chmod 755 10-home-auto
ln -s $(pwd)/10-home-auto /etc/update-motd.d/10-home-auto
ln -s $(pwd)/home-auto.txt /etc/update-motd.d/home-auto.txt



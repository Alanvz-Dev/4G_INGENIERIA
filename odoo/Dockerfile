FROM debian:stretch-slim
FROM python:3.7
LABEL authors="José Roberto Mejía Pacheco"
RUN echo 'deb http://ftp.de.debian.org/debian stretch main' > /etc/apt/sources.list
RUN echo 'deb http://deb.debian.org/debian stretch-backports main' > /etc/apt/sources.list.d/backports.list
RUN echo 'deb http://ftp.debian.org/debian/ stable main contrib non-free' > /etc/apt/sources.list.d/nonfree.list
RUN apt-get update
RUN apt-get install \
            nano \
            apt-utils \
            curl \    
            postgresql-contrib-10 \
            libsasl2-dev \
            libldap2-dev \
            libssl-dev -y --force-yes

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
COPY ./fix_install_msodbcsql17.sh /
RUN chmod a+x fix_install_msodbcsql17.sh
RUN ./fix_install_msodbcsql17.sh
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y libgssapi-krb5-2
RUN pip3 install pyodbc


RUN adduser --system --quiet --shell=/bin/bash --home=/opt/odoo --gecos 'odoo' --group odoo
RUN mkdir /etc/odoo && mkdir /var/log/odoo/
COPY ./entrypoint.sh /
COPY ./etc/odoo.conf /etc/odoo/
RUN chown odoo /etc/odoo/odoo.conf
RUN curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb
RUN echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c -
RUN apt-get install -f -y  --no-install-recommends ./wkhtmltox.deb
RUN rm -rf /var/lib/apt/lists/* wkhtmltox.deb
RUN apt-get update && apt-get install -y git
USER odoo
COPY ./4G_INGENIERIA /opt/odoo/odoo
# RUN git clone --depth 1 --branch main https://github.com/JoseRobertoMejiaPacheco/4G_INGENIERIA /opt/odoo/odoo
RUN cd /opt/odoo/odoo
USER root
RUN chown -R odoo:odoo /opt/odoo
RUN pip3 install -r /opt/odoo/odoo/requirements.txt
RUN mkdir /Filestore
RUN mkdir /Facturas
RUN su - odoo -c "/opt/odoo/odoo/odoo-bin --addons-path=/opt/odoo/odoo/addons -s --stop-after-init"
RUN ln -s /usr/local/bin/wkhtmltopdf /usr/bin/
RUN ln -s /usr/local/bin/wkhtmltoimage /usr/bin/
RUN ln -s /opt/odoo/odoo/odoo-bin /usr/bin/odoo
RUN su - odoo -c "/opt/odoo/odoo/odoo-bin --addons-path=/opt/odoo/odoo/addons -s --stop-after-init"
RUN chown -R odoo:odoo /Filestore && chmod 777 /Filestore
VOLUME ["/opt/odoo/odoo/addons", "/opt/odoo/odoo/extra_localization","/Filestore","/Facturas"]
EXPOSE 8069 8071
ENV ODOO_RC /etc/odoo/odoo.conf
WORKDIR /
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN npm i less@3.12.2 -g
RUN pip3 install xmltodict
RUN pip3 install xmltodict
RUN pip3 install pandas
RUN pip3 install  python-barcode
RUN pip3 install cfdiclient
RUN pip3 install ptvsd
RUN chown -R odoo:odoo /Filestore /Facturas && chmod 777 /Filestore /Facturas
VOLUME ["/opt/odoo/odoo/addons", "/opt/odoo/odoo/extra_localization","/Filestore","/Facturas","/etc/odoo"]
COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
USER odoo
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]




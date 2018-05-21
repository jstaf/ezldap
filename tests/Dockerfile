FROM fedora:latest
MAINTAINER Jeff Stafford <jeff.stafford@queensu.ca>

RUN dnf -y install openldap-clients openldap-servers openldap-devel \
  which psmisc procps-ng openssl

COPY directory_*.ldif /root/

# setup test ldap server
RUN cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG \
  && slapd -h "ldap:/// ldaps:/// ldapi:///" \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /root/directory_config.ldif \
  && ldapadd -H ldapi:/// -D cn=Manager,dc=ezldap,dc=io -w password -f /root/directory_base.ldif \
  # setup ldap over tls
  && openssl req -x509 -new -days 3650 -nodes \
    -keyout /etc/openldap/certs/ldap.key -out /etc/openldap/certs/ldap.crt \
    -subj "/C=CA/ST=Ontario/L=Kingston/O=ezldap/CN=ezldap.io" \
  && chown ldap. /etc/openldap/certs/ldap.* \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /root/directory_ssl.ldif

EXPOSE 389 636

ENTRYPOINT ["slapd", "-h ldap:/// ldaps:/// ldapi:///", "-d256"]

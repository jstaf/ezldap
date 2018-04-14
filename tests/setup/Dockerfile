FROM fedora:latest
MAINTAINER Jeff Stafford <jeff.stafford@queensu.ca>

RUN dnf -y install openldap-clients openldap-servers openldap-devel \
  which psmisc procps-ng

COPY directory_config.ldif .

# setup test ldap server
RUN cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG \
  && slapd -h "ldap:/// ldaps:/// ldapi:///" \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif \
  && ldapadd -Y EXTERNAL -H ldapi:/// -f directory_config.ldif

EXPOSE 389 636

ENTRYPOINT ["slapd", "-h ldap:/// ldaps:/// ldapi:///"]

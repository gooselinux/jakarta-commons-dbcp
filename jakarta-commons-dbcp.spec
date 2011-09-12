# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define base_name       dbcp
%define short_name      commons-%{base_name}
%define section         free

Name:           jakarta-commons-dbcp
Version:        1.2.1
Release:        13.8%{?dist}
Epoch:          0
Summary:        Jakarta Commons DataBase Pooling Package
License:        ASL 2.0
Group:          Development/Libraries
Source0:        http://archive.apache.org/dist/jakarta/commons/dbcp/source/commons-dbcp-1.2.1-src.tar.gz
Source5:        commons-build.tar.gz
# svn export -r '{2007-02-15}' http://svn.apache.org/repos/asf/jakarta/commons/proper/commons-build/trunk/ commons-build
# tar czf commons-build.tar.gz commons-build
Source6:        dbcp-tomcat5-build.xml
Source7:        http://repo1.maven.org/maven2/commons-dbcp/commons-dbcp/1.2.1/commons-dbcp-1.2.1.pom

Patch0:         commons-dbcp-1.2.1-project_xml.patch
Patch1:         commons-dbcp-1.2.1-TestJOCLed.patch
Patch2:         commons-dbcp-1.2.1-TestConnectionPool.patch
Patch3:         commons-dbcp-1.2.1-navigation_xml.patch
Patch4:         commons-dbcp-1.2.1-project_properties.patch
Patch5:         commons-dbcp-1.2.1-sourcever.patch
Patch6:         commons-dbcp-1.2.1-jdk6.patch

URL:            http://jakarta.apache.org/commons/%{base_name}
BuildRequires:  ant
BuildRequires:  jakarta-commons-collections >= 2.0
BuildRequires:  jakarta-commons-pool >= 1.1
BuildRequires:  jdbc-stdext >= 2.0
BuildRequires:  xerces-j2
BuildRequires:  xml-commons-apis >= 0:1.3
BuildRequires:  jpackage-utils > 1.6
BuildRequires:  junit >= 3.8
BuildRequires:  jakarta-commons-pool-tomcat5
BuildRequires:  jakarta-commons-collections-tomcat5
BuildRequires:  java-devel >= 1:1.6.0

Requires(post):  /usr/sbin/update-alternatives
Requires(preun):  /usr/sbin/update-alternatives
Requires:       jakarta-commons-collections >= 2.0
Requires:       jakarta-commons-pool >= 1.1
BuildArch:      noarch

BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Provides:   %{short_name} = %{epoch}:%{version}-%{release}
Provides:   hibernate_jdbc_cache = %{epoch}:%{version}-%{release}
Obsoletes:  %{short_name} < %{epoch}:%{version}-%{release}

%description
Many Jakarta projects support interaction with a relational
database. Creating a new connection for each user can be time
consuming (often requiring multiple seconds of clock time),
in order to perform a database transaction that might take
milliseconds. Opening a connection per user can be unfeasible
in a publicly-hosted Internet application where the number of
simultaneous users can be very large. Accordingly, developers
often wish to share a "pool" of open connections between all
of the application's current users. The number of users actually
performing a request at any given time is usually a very small
percentage of the total number of active users, and during
request processing is the only time that a database connection
is required. The application itself logs into the DBMS, and
handles any user account issues internally.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Documentation

%description javadoc
Javadoc for %{name}.

%package tomcat5
Summary:        DBCP dependency for Tomcat5
Group:          Development/Libraries

%description tomcat5
DBCP dependency for Tomcat5

%prep
%setup -q -n %{short_name}-%{version}
%{__sed} -i 's/\r//' LICENSE.txt
%{__sed} -i 's/\r//' NOTICE.txt
%{__sed} -i 's/\r//' README.txt
# quick hack
cp LICENSE.txt ../LICENSE
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
gzip -dc %{SOURCE5} | tar xf -
cp %{SOURCE6} .

%patch0 -b .sav
%patch1 -b .sav
%patch2 -b .sav
%patch3 -b .sav
%patch4 -b .sav
%patch5 -b .sav
%patch6

%build
export CLASSPATH=$(build-classpath jdbc-stdext xerces-j2)
ant \
        -Dbuild.sysclasspath=first \
        -Dcommons-pool.jar=$(build-classpath commons-pool) \
        -Dcommons-collections.jar=$(build-classpath commons-collections) \
        -Djunit.jar=$(build-classpath junit) \
        -Djndi.jar=$(build-classpath jndi) \
        -Dsax2.jar=$(build-classpath xml-commons-apis) \
        -Djava.io.tmpdir=. \
        dist test

export CLASSPATH=$(build-classpath jdbc-stdext xerces-j2 commons-collections-tomcat5 commons-pool-tomcat5)
ant -Dcompile.source=1.5 -Dant.build.javac.target=1.5 -f dbcp-tomcat5-build.xml

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
#tomcat5 jars
install -m 644 dbcp-tomcat5/%{short_name}-tomcat5.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-tomcat5-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# quick hack clean up
rm ../LICENSE

# hibernate_jdbc_cache ghost symlink
touch $RPM_BUILD_ROOT%{_javadir}/hibernate_jdbc_cache.jar

# Install pom file
install -dm 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
cp -p %{SOURCE7} $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-jakarta-commons-dbcp.pom
%add_to_maven_depmap commons-dbcp commons-dbcp %{version} JPP jakarta-commons-dbcp

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-alternatives --install %{_javadir}/hibernate_jdbc_cache.jar \
  hibernate_jdbc_cache %{_javadir}/%{name}.jar 60
%update_maven_depmap

%postun
%update_maven_depmap

%preun
{
  [ $1 -eq 0 ] || exit 0
  update-alternatives --remove hibernate_jdbc_cache %{_javadir}/%{name}.jar
} >/dev/null 2>&1 || :

%files
%defattr(-,root,root)
%doc LICENSE.txt NOTICE.txt README.txt
%{_datadir}/maven2
%{_mavendepmapfragdir}
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{short_name}.jar
%{_javadir}/%{short_name}-%{version}.jar
%ghost %{_javadir}/hibernate_jdbc_cache.jar

%files tomcat5
%defattr(-,root,root)
%{_javadir}/*-tomcat5*.jar
%doc LICENSE.txt NOTICE.txt

%files javadoc
%defattr(-,root,root)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%changelog
* Thu Jan 7 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.1-13.8
- Remove leftovers from previous maven builds.

* Thu Aug 20 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.1-13.7
- Build requires java 6.

* Thu Aug 20 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.1-13.6
- Drop gcj support.
- Fix build with java 6.
- Add maven pom.
- Drop maven1 support.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.1-13.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.1-12.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.2.1-11.5
- drop repotag

* Thu May 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.2.1-11jpp.4
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.2.1-11jpp.3
- Autorebuild for GCC 4.3

* Thu Nov 22 2007 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-10jpp.3
- Fix dangling symlink. bz#388801

* Thu Sep 20 2007 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-10jpp.2
- Rebuild

* Mon Mar 12 2007 Matt Wringe <mwringe@redhat.com> 0:1.2.1-10jpp.1
- Merger with newest jpp version
- Fix rpmlint issues
- Disable testThreaded for now as it will sometimes fail

* Fri Feb 23 2007 Jason Corley <jason.corley@gmail.com> 0:1.2.1-10jpp
- update copyright to contain current year
- rebuild on RHEL4 to avoid broken jar repack script in FC6

* Fri Jan 26 2007 Matt Wringe <mwringe@redhat.com> 0:1.2.1-9jpp
- Fix bug in dbcp-tomcat5-build.xml

* Mon Jan 22 2007 Matt Wringe <mwringe@redhat.com> 0:1.2.1-8jpp
- Add tomcat5 subpackage
- Add versioning to provides and obsoletes
- Move rm -rf %%RPM_BUILD_ROOT from %%prep to %%install
- Add missing maven plugin dependencies

* Thu Aug 17 2006 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-7jpp.1
- Added missing postun section.

* Thu Aug 10 2006 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-6jpp.1
- Added missing requirements.

* Thu Aug 10 2006 Karsten Hopp <karsten@redhat.de> 1.2.1-5jpp_4fc
- Requires(post/postun): coreutils

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 0:1.2.1-5jpp_3fc
- Rebuilt

* Thu Jul 20 2006 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-5jpp_2fc
- Rebuild.

* Thu Jul 20 2006 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-5jpp_1fc
- Added conditional native compilation.

* Wed Apr 12 2006 Ralph Apel <r.apel@r-apel.de> - 0:1.2.1-4jpp
- First JPP-1.7 release
- Build with maven by default
- Add option to build with straight ant
- Add -manual subpackage when built with maven
- Backported TestJOCLed from HEAD

* Tue Nov 02 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.2.1-3jpp
- Bump release to make provide hibernate_jdbc_cache official

* Tue Aug 24 2004 Randy Watler <rwatler at finali.com> - 0:1.2.1-0.hjc.2jpp
- Rebuild with ant-1.6.2

* Fri Jul 02 2004 Ralph Apel <r.apel at r-apel.de> 0:1.2.1-0.hjc.1jpp
- Provide hibernate_jdbc_cache and di update-alternatives, prio 60

* Thu Jun 24 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:1.2.1-1jpp
- Update to 1.2.1 (tomcat 5.0.27 wants it)

* Mon Oct 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.1-1jpp
- common-dbcp 1.1

* Tue Mar 25 2003 Nicolas Mailhot <Nicolas.Mailhot (at) JPackage.org> 1.0-4jpp
- for jpackage-utils 1.5

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0-3jpp
- fix ASF license

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0-2jpp
- fix missing packager tag

* Fri Aug 23 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-1jpp
- 1.0 release

* Fri Jul 12 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-3jpp
- add require xml-commons-apis
- override java.io.tmpdir to avoid build use /tmp

* Mon Jun 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-2jpp
- use sed instead of bash 2.x extension in link area to make spec compatible
  with distro using bash 1.1x

* Fri Jun 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-1jpp
- 1.0 (cvs 20020606)
- added short names in %%{_javadir}, as does jakarta developpers
- first jPackage release

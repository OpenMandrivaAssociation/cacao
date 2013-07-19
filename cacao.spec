%define section         free

%define priority        1500
%define javaver         1.5.0
%define buildver        0

%define _libdir         %{_prefix}/%{_lib}/%{name}

%define java_version    %{javaver}.%{buildver}

%define origin          cacao
%define originver       0.99.4
%define cname           java-%{javaver}-%{origin}

%define sdklnk          java-%{javaver}-%{origin}
%define jrelnk          jre-%{javaver}-%{origin}
%define sdkdir          %{cname}-%{java_version}
%define jredir          %{sdkdir}/jre
%define sdkbindir       %{_jvmdir}/%{sdklnk}/bin
%define jrebindir       %{_jvmdir}/%{jrelnk}/bin
%define jvmjardir       %{_jvmjardir}/%{cname}-%{java_version}

Name:           cacao
Version:        1.6.0
Release:        1
Epoch:          0
Summary:        JIT compiler for Java
Group:          Development/Java
License:        GPLv2
URL:            http://www.cacaojvm.org/
Source0:        http://www.complang.tuwien.ac.at/cacaojvm/download/cacao-1.6.0/%{name}-%{version}.tar.xz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:  automake1.8
BuildRequires:  binutils-devel
BuildRequires:  classpath-devel >= 0:0.90
BuildRequires:  eclipse-ecj
BuildRequires:  java-1.5.0-gcj-devel
BuildRequires:  java-rpmbuild >= 0:1.5, sed
BuildRequires:  libltdl-devel
BuildRequires:  tetex
BuildRequires:  tetex-latex
Requires:       gcj-tools
Requires:       jce
Requires:       java-sasl
Requires(post): classpath >= 0:0.90
Requires(postun): classpath >= 0:0.90
Requires(post): jpackage-utils >= 0:1.6.3
Requires(postun): jpackage-utils >= 0:1.6.3
Requires(post): gcj-tools
Requires(postun): gcj-tools
Provides:       jre-%{javaver}-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       jre-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       jre-%{javaver}, java-%{javaver}, jre = %{epoch}:%{javaver}
Provides:       java-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       java = %{epoch}:%{javaver}
Provides:       jaxp_parser_impl
Provides:       jndi, jndi-ldap, jdbc-stdext, jaas, jta
Provides:       jsse
Provides:       jaxp_transform_impl
Obsoletes:      java-%{javaver}-%{origin}
Provides:       java-%{javaver}-%{origin}
#Provides:      %{origin} = %{epoch}:%{originver}

%description
CACAO is a JIT compiler for Java. The CACAO project started as a 
research JavaVM to explore new implementation techniques. The first 
version for the Alpha was released in February 1997 as a binary. After 
1998 the development nearly stopped. Since two years we are actively 
working on CACAO again and are proud to announce the first source 
release under the GPL.

%prep
%setup -q

%build
export CLASSPATH=
%{configure2_5x} \
  --disable-rpath \
  --with-java-runtime-library=gnuclasspath \
  --with-java-runtime-library-prefix=%{_prefix} \
  --with-java-runtime-library-libdir=%{_libdir}
%{make}
(cd doc/handbook && %{__make} handbook)

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}
%{__rm} %{buildroot}%{_bindir}/java

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin
(cd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin %{__ln_s} %{_bindir}/%{origin} java)

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib

# create extensions symlinks
# jessie
ln -s %{_datadir}/classpath/glibj.zip $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/jsse.jar

# extensions handling
install -dm 755 $RPM_BUILD_ROOT%{jvmjardir}
pushd $RPM_BUILD_ROOT%{jvmjardir}
   ln -s %{_jvmdir}/%{jredir}/lib/jaas.jar jaas-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jdbc-stdext.jar jdbc-stdext-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jndi.jar jndi-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jsse.jar jsse-%{java_version}.jar
   for jar in *-%{java_version}.jar ; do
     ln -sf ${jar} $(echo $jar | sed "s|-%{java_version}.jar|-%{javaver}.jar|g")
     ln -sf ${jar} $(echo $jar | sed "s|-%{java_version}.jar|.jar|g")
   done
popd

# versionless symlinks
pushd $RPM_BUILD_ROOT%{_jvmdir}
   ln -s %{jredir} %{jrelnk}
#   ln -s %{sdkdir} %{sdklnk}
popd

pushd $RPM_BUILD_ROOT%{_jvmjardir}
   ln -s %{sdkdir} %{jrelnk}
#   ln -s %{sdkdir} %{sdklnk}
popd

# generate file lists
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type d \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' >  %{name}-%{version}-all.files
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type f -o -type l \
  | sed 's|'$RPM_BUILD_ROOT'||'      >> %{name}-%{version}-all.files

cat %{name}-%{version}-all.files \
  > %{name}-%{version}.files

find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/bin -type f -o -type l \
  | sed "s|^$RPM_BUILD_ROOT||"      > %{name}-%{version}-sdk-bin.files

%{__rm} -rf %{buildroot}%{_includedir}

%clean
%{__rm} -rf %{buildroot}

%post
update-alternatives \
  --install %{_bindir}/java java %{_jvmdir}/%{jrelnk}/bin/java %{priority} \
  --slave %{_jvmdir}/jre          jre          %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre       jre_exports  %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/rmiregistry  rmiregistry  %{_jvmdir}/%{jrelnk}/bin/rmiregistry

update-alternatives \
  --install %{_jvmdir}/jre-%{origin} \
      jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{origin} \
      jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}

update-alternatives \
  --install %{_jvmdir}/jre-%{javaver} \
      jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{javaver} \
      jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}

# rt.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/rt.jar

# jaas.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jaas.jar

# jdbc-stdext.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jdbc-stdext.jar

# jndi.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jndi.jar

# jaxp_parser_impl
update-alternatives --install %{_javadir}/jaxp_parser_impl.jar \
  jaxp_parser_impl \
  %{_datadir}/classpath/glibj.zip 20

# jaxp_transform_impl
update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
  jaxp_transform_impl \
  %{_datadir}/classpath/glibj.zip 20

%postun
if [ $1 -eq 0 ] ; then
   update-alternatives --remove java %{_jvmdir}/%{jrelnk}/bin/java
   update-alternatives --remove jre_%{origin}  %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jaxp_parser_impl \
     %{_datadir}/classpath/glibj.zip
   update-alternatives --remove jaxp_transform_impl \
     %{_datadir}/classpath/glibj.zip
fi

%files -f %{name}-%{version}.files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog* COPYING INSTALL NEWS README THIRDPARTY doc/handbook/%{origin}.dvi
%dir %{_jvmdir}/%{sdkdir}
%dir %{jvmjardir}
%{jvmjardir}/*.jar
%{_jvmdir}/%{jrelnk}
%{_jvmjardir}/%{jrelnk}
%{_bindir}/%{origin}
%{_datadir}/%{origin}
%{_mandir}/man1/%{origin}.1*
%{_libdir}/libjvm*


%changelog
* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 0:0.99.4-2mdv2011.0
+ Revision: 610092
- rebuild

* Mon Feb 15 2010 Sandro Cazzaniga <kharec@mandriva.org> 0:0.99.4-1mdv2010.1
+ Revision: 506125
- update to 0.99.4

* Wed Sep 02 2009 Thierry Vignaud <tv@mandriva.org> 0:0.99.3-2mdv2010.0
+ Revision: 424721
- rebuild

* Sat Aug 16 2008 David Walluck <walluck@mandriva.org> 0:0.99.3-1mdv2009.0
+ Revision: 272770
- 0.99.3

* Sat Aug 09 2008 David Walluck <walluck@mandriva.org> 0:0.99.2-1mdv2009.0
+ Revision: 270072
- fix build
- 0.99.2

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Anssi Hannula <anssi@mandriva.org>
    - buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sat Jul 21 2007 David Walluck <walluck@mandriva.org> 0:0.98-3mdv2008.0
+ Revision: 54248
- more alternatives fixing

* Sat Jul 21 2007 David Walluck <walluck@mandriva.org> 0:0.98-2mdv2008.0
+ Revision: 54183
- fix build
- fix jsse link
- fix java link

* Sun Jun 10 2007 David Walluck <walluck@mandriva.org> 0:0.98-1mdv2008.0
+ Revision: 37936
- 0.98
- supports java 1.5.0


* Fri Nov 10 2006 David Walluck <walluck@mandriva.org> 0.97-2mdv2007.0
+ Revision: 80538
- fix classpath-libdir

* Thu Nov 09 2006 David Walluck <walluck@mandriva.org> 0:0.97-1mdv2007.1
+ Revision: 79926
- fix libjvm location

* Thu Nov 02 2006 David Walluck <walluck@mandriva.org> 0:0.97-0.5891.1mdv2007.1
+ Revision: 75108
- 0.97 (SVN 5891)

* Fri Oct 27 2006 David Walluck <walluck@mandriva.org> 0:0.97-0.5824.1mdv2007.1
+ Revision: 72965
- SVN 5824

* Mon Oct 23 2006 David Walluck <walluck@mandriva.org> 0:0.96-2mdv2007.1
+ Revision: 71668
- Import cacao

* Mon Aug 14 2006 Emmanuel Andry <eandry@mandriva.org> 0:0.96-2mdv2007.0
- 0.96
- rebuild to fix dependencies

* Fri May 26 2006 David Walluck <walluck@mandriva.org> 0:0.96-1mdv2007.0mdk
- 0.96
- rebuild to fix dependencies

* Sat May 13 2006 David Walluck <walluck@mandriva.org> 0:0.95-5mdk
- SVN 4908
- rebuild for new binutils

* Tue Apr 25 2006 David Walluck <walluck@mandriva.org> 0:0.95-4mdk
- SVN 4831

* Wed Apr 12 2006 David Walluck <walluck@mandriva.org> 0:0.95-3mdk
- update to SVN 20060411 for classpath 0.90 support
- BuildRequires: classpath-devel not classpath

* Wed Apr 12 2006 David Walluck <walluck@mandriva.org> 0:0.95-2mdk
- rebuild to fix dependencies

* Thu Feb 16 2006 David Walluck <walluck@mandriva.org> 0:0.95-1mdk
- 0.95

* Mon Feb 13 2006 David Walluck <walluck@mandriva.org> 0:0.94-3mdk
- SVN 20060213
- BuildRequires: java-devel
- export JAR

* Tue Jan 31 2006 David Walluck <walluck@mandriva.org> 0:0.94-2mdk
- fix classpath libdir

* Tue Jan 31 2006 David Walluck <walluck@mandriva.org> 0:0.94-1mdk
- 0.94 (SVN 20060130)

* Thu Jan 19 2006 David Walluck <walluck@mandriva.org> 0:0.93-7mdk
- BuildRequires: libltdl-devel

* Wed Jan 18 2006 David Walluck <walluck@mandriva.org> 0:0.93-6mdk
- BuildRequires: automake1.8
- BuildRequires (not Requires): binutils-devel
- --disable-jvmti

* Sun Jan 15 2006 David Walluck <walluck@mandriva.org> 0:0.93-5mdk
- CVS (20050114)
- BuildRequires: jikes

* Sat Jan 14 2006 David Walluck <walluck@mandriva.org> 0:0.93-4mdk
- really fix library path on x86_64

* Sat Jan 14 2006 David Walluck <walluck@mandriva.org> 0:0.93-3mdk
- fix library path on x86_64

* Sat Jan 14 2006 David Walluck <walluck@mandriva.org> 0:0.93-2mdk
- add java and rmiregistry symlinks

* Fri Jan 13 2006 David Walluck <walluck@mandriva.org> 0:0.93-1mdk
- release



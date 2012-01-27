# TODO:
#	- trigger to clean up after old bird package (stop, chkconfig --del)
#
# Conditional build:
%bcond_without	ipv6	# disable IPv6 support (and building bird-ipv6 package)
%bcond_without	ipv4	# disable IPv4 support (and building bird-ipv4 package)
%bcond_with	alien	# enable possibility to import 'alien' routes import into bird's routing table
#
Summary:	The BIRD Internet Routing Daemon
Summary(pl.UTF-8):	Demon BIRD Internetowego Routingu Dynamicznego
Name:		bird
Version:	1.3.6
Release:	3
License:	GPL v2+
Group:		Networking/Daemons
Source0:	ftp://bird.network.cz/pub/bird/%{name}-%{version}.tar.gz
# Source0-md5:	fa5621a41dcd86b6cb8cbe4fbd74af7e
Source1:	%{name}-ipv4.init
Source2:	%{name}-ipv4.sysconfig
Source3:	%{name}-ipv6.init
Source4:	%{name}-ipv6.sysconfig
Source5:	ftp://bird.network.cz/pub/bird/%{name}-doc-%{version}.tar.gz
# Source5-md5:	88fa1713bfb0fedc2be9e078f22bd437
Patch0:		%{name}-allowalien.patch
URL:		http://bird.network.cz/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	bird-daemon
Requires:	rc-scripts
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/usr/sbin/useradd
Obsoletes:	gated
Obsoletes:	mrt
Obsoletes:	zebra
Obsoletes:	zebra-guile
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The BIRD project is an attempt to create a routing daemon running on
UNIX-like systems (but not necessarily limited to them) with full
support of all modern routing protocols, easy to use configuration
interface and powerful route filtering language.

%description -l pl.UTF-8
Projekt BIRD ma na celu utworzenie daemona dynamicznego routingu
pracującego na systemach UNIX z pełnym wsparciem dla nowoczesnych
protokołów routingu, łatwym interfejsem konfiguracji i językiem
filtrów o dużych możliwościach.

%package ipv4
Summary:	Routing daemon for IPv4
Summary(pl.UTF-8):	Demon dynamicznego routingu IPv4
Group:		Networking/Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	rc-scripts
Provides:	bird-daemon
Provides:	routingdaemon
Obsoletes:	gated
Obsoletes:	mrt
Obsoletes:	zebra
Obsoletes:	zebra-guile

%description ipv4
The BIRD project is an attempt to create a routing daemon running on
UNIX-like systems (but not necessarily limited to them) with full
support of all modern routing protocols, easy to use configuration
interface and powerful route filtering language.

%description ipv4 -l pl.UTF-8
Projekt BIRD ma na celu utworzenie daemona dynamicznego routingu
pracującego na systemach UNIX z pełnym wsparciem dla nowoczesnych
protokołów routingu, łatwym interfejsem konfiguracji i językiem
filtrów o dużych możliwościach.

%package ipv6
Summary:	Routing daemon for IPv6
Summary(pl.UTF-8):	Demon dynamicznego routingu IPv6
Group:		Networking/Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	rc-scripts
Provides:	bird-daemon
Provides:	routingdaemon
Obsoletes:	gated
Obsoletes:	mrt
Obsoletes:	zebra
Obsoletes:	zebra-guile

%description ipv6
The BIRD project is an attempt to create a routing daemon running on
UNIX-like systems (but not necessarily limited to them) with full
support of all modern routing protocols, easy to use configuration
interface and powerful route filtering language.

%description ipv6 -l pl.UTF-8
Projekt BIRD ma na celu utworzenie daemona dynamicznego routingu
pracującego na systemach UNIX z pełnym wsparciem dla nowoczesnych
protokołów routingu, łatwym interfejsem konfiguracji i językiem
filtrów o dużych możliwościach.

%prep
%setup -q -a 5
%{?with_alien:%patch0 -p1}

%build
cp -f /usr/share/automake/config.* tools
%{__autoconf}

export CFLAGS="%{rpmcflags} -I%{_includedir}/ncursesw"

%if %{with ipv6}
%configure \
	--disable-memcheck \
	--enable-client \
	--enable-ipv6
%{__make} -j1

mv bird bird-6

%{__make} clean
%endif

%if %{with ipv4}
%configure \
	--disable-memcheck \
	--enable-client \
	--disable-ipv6
%{__make} -j1
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,%{_sbindir}}

install birdc $RPM_BUILD_ROOT%{_sbindir}

%if %{with ipv4}
install bird $RPM_BUILD_ROOT%{_sbindir}
install doc/bird.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}-ipv4
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}-ipv4
%endif

%if %{with ipv6}
install bird-6 $RPM_BUILD_ROOT%{_sbindir}
cat <<EOF > $RPM_BUILD_ROOT%{_sbindir}/birdc-6
#!/bin/sh
exec %{_sbindir}/birdc -s /var/run/bird6.ctl
EOF
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}-ipv6
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}-ipv6
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 271 bird
%useradd -u 271 -d /usr/share/empty -s /bin/false -c "bird routing daemon" -g bird bird

%postun
if [ "$1" = "0" ]; then
	%userremove bird
	%groupremove bird
fi

%post ipv4
/sbin/chkconfig --add %{name}-ipv4
%service %{name}-ipv4 restart "routing daemon"

%preun ipv4
if [ "$1" = "0" ]; then
	%service %{name}-ipv4 stop
	/sbin/chkconfig --del %{name}-ipv4
fi

%post ipv6
/sbin/chkconfig --add %{name}-ipv6
%service %{name}-ipv6 restart "routing daemon"

%preun ipv6
if [ "$1" = "0" ]; then
	%service %{name}-ipv6 stop
	/sbin/chkconfig --del %{name}-ipv6
fi

%triggerpostun ipv4 -- %{name}-ipv4 < 1.3.4-3
chmod 0640 /etc/bird.conf
chgrp bird /etc/bird.conf

%files
%defattr(644,root,root,755)
%doc doc/*.html doc/reply_codes %{name}-doc-%{version}/doc/*.ps ChangeLog NEWS README TODO
%attr(755,root,root) %{_sbindir}/birdc

%if %{with ipv4}
%files ipv4
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/bird
%attr(754,root,root) /etc/rc.d/init.d/bird-ipv4
%attr(644,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/bird-ipv4
%attr(640,root,bird) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/bird.conf
%endif

%if %{with ipv6}
%files ipv6
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/bird-6
%attr(755,root,root) %{_sbindir}/birdc-6
%attr(754,root,root) /etc/rc.d/init.d/bird-ipv6
%attr(644,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/bird-ipv6
#%attr(640,root,bird) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/bird-6.conf
%endif

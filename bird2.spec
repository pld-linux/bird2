# Conditional build:
%bcond_without	docs		# don't build html docs
%bcond_without	libssh		# disable libssh support in RPKI
%bcond_without	mpls_kernel	# disable MPLS support in kernel protocol
#
Summary:	The BIRD Internet Routing Daemon
Summary(pl.UTF-8):	Demon BIRD Internetowego Routingu Dynamicznego
Name:		bird2
Version:	2.0.10
Release:	0.1
License:	GPL v2+
Group:		Networking/Daemons
Source0:	https://bird.network.cz/download/bird-%{version}.tar.gz
# Source0-md5:	1026621839e0162844afa991ad9a7355
Source1:	https://bird.network.cz/download/bird-doc-%{version}.tar.gz
# Source1-md5:	ad099b03849730aa7bd6931b89dae490
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Source4:	%{name}.service
URL:		https://bird.network.cz/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
%{?with_libssh:BuildRequires:	libssh-devel}
%{?with_docs:BuildRequires:	opensp}
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rpmbuild(macros) >= 1.268
%{?with_docs:BuildRequires:	sgmls}
%{?with_docs:BuildRequires:	sgml-tools}
%{?with_docs:BuildRequires:	texlive-format-pdflatex}
%{?with_docs:BuildRequires:	texlive-latex-enumitem}
%{?with_docs:BuildRequires:	texlive-xetex}
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/usr/sbin/useradd
Obsoletes:	bird-ipv4
Obsoletes:	bird-ipv6
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

%prep
%setup -q -n bird-%{version} -a 1

%build
cp -f /usr/share/automake/config.* tools
%{__autoconf}

%configure \
	--disable-memcheck \
	--enable-client \
	%{__enable_disable libssh libssh} \
	%{__enable_disable mpls_kernel mpls-kernel} \

%{__make}
%{?with_docs:%{__make} docs}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,%{_sbindir}} \
	$RPM_BUILD_ROOT%{systemdunitdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/bird
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/bird
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/bird.service

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 271 bird
%useradd -u 271 -d /usr/share/empty -s /bin/false -c "bird routing daemon" -g bird bird

%post
/sbin/chkconfig --add bird
%service bird restart "routing daemon"
%systemd_post bird.service

%preun
if [ "$1" = "0" ]; then
	%service bird stop
	/sbin/chkconfig --del bird
fi
%systemd_preun bird.service

%postun
if [ "$1" = "0" ]; then
	%userremove bird
	%groupremove bird
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc %{?with_docs:obj/doc/*.html} doc/reply_codes bird-doc-%{version}/doc/*.pdf ChangeLog NEWS README 
%attr(755,root,root) %{_sbindir}/bird
%attr(755,root,root) %{_sbindir}/birdc
%attr(755,root,root) %{_sbindir}/birdcl
%attr(754,root,root) /etc/rc.d/init.d/bird
%attr(644,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/bird
%attr(640,root,bird) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/bird.conf
%{systemdunitdir}/bird.service

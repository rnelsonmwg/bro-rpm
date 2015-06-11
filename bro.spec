Name:             bro
Version:          2.3.2
Release:          5%{?dist}
Summary:          A Network Intrusion Detection System and Analysis Framework

License:          BSD
URL:              http://bro.org
Source0:          http://www.bro.org/downloads/release/%{name}-%{version}.tar.gz
Source1:          bro.service
Source2:          bro-logrotate.conf
# Fix for the usage of configure with cmake. This is Fedora specific.
Patch0:           bro-2.3-configure.patch
# The aux tools are separate packages. No need to build them.
Patch1:           bro-2.3-broctl-disable-aux.patch
# Adjust the paths
Patch2:           bro-2.3-broctl-path.patch
Patch3:           bro-1.5.1-format-security.patch

BuildRequires:    cmake
BuildRequires:    libpcap-devel
BuildRequires:    openssl-devel
BuildRequires:    zlib-devel
BuildRequires:    ncurses-devel
BuildRequires:    curl-devel
BuildRequires:    libtool
BuildRequires:    byacc
Buildrequires:    swig
BuildRequires:    bison
BuildRequires:    flex
BuildRequires:    file-devel
BuildRequires:    libxml2-devel
BuildRequires:    readline-devel
%ifnarch s390 s390x
BuildRequires:    gperftools-devel
%endif
BuildRequires:    bind-devel
BuildRequires:    jemalloc-devel
BuildRequires:    python2-devel
BuildRequires:    python-tools
BuildRequires:    GeoIP-devel
BuildRequires:    systemd
# Unfortunately there is check for sendmail during prep
#BuildRequires:    sendmail

BuildRequires:    pysubnettree
BuildRequires:    trace-summary
BuildRequires:    capstats

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Requires:         broctl

%description
Bro is an open-source, Unix-based Network Intrusion Detection System (NIDS)
that passively monitors network traffic and looks for suspicious activity.
Bro detects intrusions by first parsing network traffic to extract is
application-level semantics and then executing event-oriented analyzers that
compare the activity with patterns deemed troublesome. Its analysis includes
detection of specific attacks (including those defined by signatures, but also
those defined in terms of events) and unusual activities (e.g., certain hosts
connecting to certain services, or patterns of failed connection attempts).

%package -n binpac
Summary:        A language for protocol parsers

%description -n binpac
BinPAC is a high level language for describing protocol parsers and generates
C++ code. It is currently maintained and distributed with the Bro Network
Security Monitor distribution, however, the generated parsers may be used
with other programs besides Bro.

%package -n binpac-devel
Summary:        Development file for binpac
Requires:       binpac = %{version}-%{release}
Provides:       binpac-static = %{version}-%{release}

%description -n binpac-devel
This package contains the header files for binpac.

%package -n broctl
Summary:          A control tool for bro
Buildarch:        noarch

%description -n broctl
BroControl is an interactive interface for managing a Bro installation which
allows you to, e.g., start/stop the monitoring or update its configuration.

%package -n broccoli
Summary:          The bro client communication library
Requires:         bro = %{version}-%{release}

%description -n broccoli
Broccoli is the "Bro client communications library". It allows you to create
client sensors for the Bro intrusion detection system. Broccoli can speak a
good subset of the Bro communication protocol, in particular, it can receive
Bro IDs, send and receive Bro events, and send and receive event requests
to/from peering Bros. You can currently create and receive values of pure
types like integers, counters, timestamps, IP addresses, port numbers,
booleans, and strings.

%package -n broccoli-devel
Summary:          Development file for broccoli

Requires:         bro = %{version}-%{release}
Requires:         pkgconfig

%description -n broccoli-devel
This package contains the header files for broccoli.

%package -n python-broccoli
Summary:          Python bindings for bro

BuildRequires:    python2-devel

Requires:         bro = %{version}-%{release}
Requires:         pysubnettree
Requires:         trace-summary
Requires:         capstats

%description -n python-broccoli
This Python module provides bindings for Broccoli, Bro’s client communication
library.

%package doc
Summary:          Documentation for bro

BuildRequires:    python-sphinx
BuildRequires:    doxygen
BuildRequires:    rsync

%description doc
This package contains the documentation for bro.

%prep
%setup -q
%patch0 -p1 -b .configure
%patch1 -p1 -b .cmake
%patch2 -p1 -b .path
#%patch3 -p1 -b .format

# Paths for broctl broctl/bin/broctl.in
sed -ibak "s|/lib/broctl|%{python2_sitelib}/BroControl|g" aux/broctl/BroControl/options.py
sed -ibak "s|/lib|%{_libdir}/bro|g" aux/broctl/BroControl/options.py

# Shebang
sed -i -e '1i#! /usr/bin/bash' aux/broctl/bin/set-bro-path aux/broctl/bin/helpers/to-bytes.awk

%build
%configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --conf-files-dir=%{_sysconfdir}/bro \
    --python-install-dir=%{python2_sitelib} \
    --disable-rpath \
    --enable-debug \
    --enable-mobile-ipv6 \
    --enable-jemalloc \
    --enable-binpac
make %{?_smp_mflags}
make doc
# Fix doc related rpmlint issues
rm -rf %{_builddir}/%{name}-%{version}/build/doc/sphinx_output/html/.tmp
rm -rf %{_builddir}/%{name}-%{version}/build/doc/sphinx_output/html/.buildinfo
rm -rf %{_builddir}/%{name}-%{version}/build/doc/sphinx_output/html/_static/broxygen-extra.js
find %{_builddir}/%{name}-%{version}/build/doc/ -size 0 -delete
sed -i "s|\r||g" %{_builddir}/%{name}-%{version}/build/doc/sphinx_output/html/objects.inv
f="%{_builddir}/%{name}-%{version}/build/doc/sphinx_output/html/objects.inv"
iconv --from=ISO-8859-1 --to=UTF-8 $f > $f.new && \
touch -r $f $f.new && \
mv $f.new $f

%install
make install DESTDIR=%{buildroot} INSTALL="install -p"

# Install service file
%{__install} -D -c -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/bro.service

# Install config
%{__install} -d -m 755 %{buildroot}%{_sysconfdir}/bro

# Create runtime dir
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/run/bro

# Create log dirs
install -D -m 0644 -p %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/bro
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/archive
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/sorted-logs
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/stats

# Create spool dir
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/spool/bro
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/spool/bro/tmp

# Install scripts
pushd scripts
%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/scripts
popd

# The signature samples should go into a seperate sub-package if possible
# Install example signatures, site policy
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/site
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/host

# Fix broctl python location
mv %{buildroot}/usr/lib/broctl/BroControl/ %{buildroot}%{python2_sitelib}/BroControl/
mv %{buildroot}/usr/lib/broctl/plugins %{buildroot}%{python2_sitelib}/BroControl/plugins

# Move static library to default location
%if 0%{?__isa_bits} == 64
mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}/usr/lib/libbinpac.a %{buildroot}%{_libdir}/libbinpac.a
%endif

# Remove devel, junk, and zero length files
find "%{buildroot}%{_prefix}" -iname "*.la" -delete;
#find "%{buildroot}%{_prefix}" -iname "*.[ha]" -delete;
find "%{buildroot}" -iname "*.log" -delete;
rm -rf %{buildroot}%{_includedir}/binpac.h.in

%post
/sbin/ldconfig
%systemd_post bro.service

%preun
%systemd_preun bro.service

%postun
%systemd_postun bro.service

%postin -n broccoli
/sbin/ldconfig

%postin -n broccoli-devel
/sbin/ldconfig

%postun -n broccoli
/sbin/ldconfig

%check
make test

%files
%doc CHANGES COPYING NEWS README VERSION
%{_bindir}/bro
%{_bindir}/bro-cut
%config(noreplace) %{_sysconfdir}/bro/networks.cfg
%config(noreplace) %{_sysconfdir}/bro/node.cfg
%{_unitdir}/bro.service
%{_datadir}/bro/

%config(noreplace) %{_sysconfdir}/logrotate.d/bro
#%ghost %{_localstatedir}/run/bro
%ghost %{_localstatedir}/log/bro
%ghost %{_localstatedir}/lib/bro
%ghost %{_localstatedir}/spool/bro

%files -n binpac
%doc CHANGES COPYING README
%{_bindir}/binpac

%files -n binpac-devel
%{_includedir}/binpac*.h
%{_libdir}/libbinpac.a

%files -n broctl
%config(noreplace) %{_sysconfdir}/bro/broctl.cfg
%config(noreplace) %{_sysconfdir}/bro/node.cfg
%{_bindir}/broctl
%{python2_sitelib}/BroControl
%{_datadir}/broctl/

%files -n broccoli
%config(noreplace) %{_sysconfdir}/bro/broccoli.conf
%{_libdir}/libbroccoli.so.*

%files -n broccoli-devel
%{_bindir}/broccoli-config
%{_libdir}/libbroccoli.so
%{_includedir}/broccoli.h
%exclude %{_libdir}/libbroccoli.a

%files -n python-broccoli
%{python2_sitelib}/*broccoli*

%files doc
%doc doc/LICENSE doc/README
%doc build/doc/sphinx_output/html

%changelog
* Thu Jun 11 2015 Dan Horák <dan[at]danny.cz> - 2.3.2-5
- gperftools not available on s390(x)

* Thu May 28 2015 Fabian Affolter <mail@fabian-affolter.ch> - 2.3.2-4
- Fix requirements (rhbz#1220801)

* Tue Apr 28 2015 Peter Robinson <pbrobinson@fedoraproject.org> 2.3.2-3
- Fix NVR requires

* Mon Apr 20 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 2.3.2-2
- x86-64 is not the only one 64-bit architecture in Fedora (rhbz#1213420)

* Tue Mar 03 2015 Fabian Affolter <mail@fabian-affolter.ch> - 2.3.2-1
- Update to latest upstream version 2.3.2

* Fri Jan 23 2015 Fabian Affolter <mail@fabian-affolter.ch> - 2.3.1-1
- Update to latest upstream version 2.3.1 (rhbz#1140090)

* Fri Aug 15 2014 Fabian Affolter <mail@fabian-affolter.ch> - 2.3-1
- Introduce logrotate
- Move docs, python bindings, broctl, and broccoli to subpackage
- Update systemd macros (rhbz#850051)
- Add ghost (rhbz#656552)
- capstats, trace-summary, pysubnettree, btest, and binpac are separate packages
- Update to latest upstream version 2.3 (rhbz#979726)

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 1.5.1-11
- Fix FTBFS with -Werror=format-security (#1037005, #1106016)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild
- BR: systemd-units for %%{_unitdir} macro definition

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1.5.1-8
- Perl 5.18 rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 18 2012 Jon Ciesla <limburgher@gmail.com> - 1.5.1-5
- Migrate to systemd, BZ 771767.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 jkeating - 1.5.1-2
- Rebuilt for gcc bug 634757

* Wed Sep  8 2010 Daniel Kopecek <dkopecek@redhat.com> - 1.5.1-1
- update to new upstream version

* Tue Aug 25 2009 Tomas Mraz <tmraz@redhat.com> - 1.4-0.6.20080804svn
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-0.5.20080804svn
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-0.4.20080804svn
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> - 1.4-0.3.20080804svn
- rebuild with new openssl

* Tue Aug 26 2008 Daniel Kopecek <dkopecek@redhat.com> - 1.4-0.2.20080804svn
- Added patch to prevent collision with the internal
  variable in Autoconf 2.62. Thanks to skasal@redhat.com.

* Wed May  7 2008 Daniel Kopecek <dkopecek@redhat.com> - 1.4-0.1.20080804svn
- Initial build.

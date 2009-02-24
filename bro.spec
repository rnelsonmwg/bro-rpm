%define snapshot 20080804

Summary: Open-source, Unix-based Network Intrusion Detection System
Name: bro
Version: 1.4
Release: 0.4.%{snapshot}svn%{?dist}
License: BSD
Group: Applications/Internet
URL: http://bro-ids.org

# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#  svn export -r 6043 http://svn.icir.org/bro/trunk/bro bro-%{snapshot}
#  tar -czvf bro-%{snapshot}.tgz bro-%{snapshot}

Source0: bro-%{snapshot}.tgz
Source1: bro-%{snapshot}.cfg
Source2: bro-%{snapshot}.rc
Patch0: bro-%{snapshot}-installpolicy.patch
Patch1: bro-%{snapshot}-configurein.patch
Patch2: bro-20080804-configure-opt-check.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libpcap-devel openssl-devel zlib-devel ncurses-devel automake autoconf libtool flex bison file-devel bind-devel

Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts

%description
Bro is an open-source, Unix-based Network Intrusion Detection System (NIDS)
that passively monitors network traffic and looks for suspicious activity.
Bro detects intrusions by first parsing network traffic to extract is
application-level semantics and then executing event-oriented analyzers that
compare the activity with patterns deemed troublesome. Its analysis includes
detection of specific attacks (including those defined by signatures, but also
those defined in terms of events) and unusual activities (e.g., certain hosts
connecting to certain services, or patterns of failed connection attempts).

%prep
%setup -q -n %{name}-%{snapshot}
%patch0 -p1 -b .installpolicy
%patch1 -p1 -b .configurein
%patch2 -p1 -b .optcheck

%build
./autogen.sh
%configure --enable-brov6 --disable-broccoli
%{__make} %{?_smp_mflags} CFLAGS+="-I/usr/include/ncurses"

%install
rm -rf %{buildroot}
%{__make} DESTDIR="%{buildroot}" install

# Install config
%{__install} -d -m 755 %{buildroot}%{_sysconfdir}/bro
%{__install} -D -c -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/bro

# Create runtime dir
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/run/bro

# Create log dirs
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/archive
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/sorted-logs

# Install scripts
cd scripts/
%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/scripts
%{__install} -c -m 644 bro.rc-hooks.sh  %{buildroot}%{_datadir}/bro/scripts/bro.rc-hooks.sh 
%{__install} -D -c -m 755 %{SOURCE2}    %{buildroot}%{_initrddir}/bro

%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/scripts/s2b
%{__install} -c -m 755 snort2bro/snort2bro      %{buildroot}%{_datadir}/bro/scripts/s2b/snort2bro
%{__install} -c -m 644 snort2bro/snort2bro.cfg  %{buildroot}%{_datadir}/bro/scripts/s2b/snort2bro.cfg
cd ..

# Install bifs
#%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/bif
#cd src/
#for bif in $(ls *.bif.bro); do
#    %{__install} -c -m 644 ${bif} %{buildroot}%{_datadir}/bro/bif/${bif}
#done
#cd ..

# Install example signatures, site policy
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/site
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/host
%{__install} -c -m 644 scripts/s2b/example_bro_files/signatures.sig     %{buildroot}%{_localstatedir}/lib/bro/site/signatures.sig
%{__install} -c -m 644 scripts/local.lite.bro                           %{buildroot}%{_localstatedir}/lib/bro/site/localhost.bro

rm -rf src/libedit

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add bro

%preun
if [ $1 = 0 ] ; then
    /sbin/service bro stop >/dev/null 2>&1
    /sbin/chkconfig --del bro
fi

%files
%defattr(-,root,root,-)
%doc README COPYING doc/user-manual/Bro-user-manual.pdf doc/ref-manual/Bro-Ref-Manual.pdf doc/quick-start/Bro-quick-start.pdf doc/pubs/*.ps doc/misc/*
%config(noreplace) %{_sysconfdir}/sysconfig/bro
%{_initrddir}/bro
%{_bindir}/bro
%{_datadir}/bro
%{_localstatedir}/run/bro
%{_localstatedir}/log/bro
%{_localstatedir}/lib/bro

%changelog
* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-0.4.20080804svn
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> - 1.4-0.3.20080804svn
- rebuild with new openssl

* Tue Aug 26 2008 Daniel Kopecek <dkopecek@redhat.com> - 1.4-0.2.20080804svn
- Added patch to prevent collision with the internal
  variable in Autoconf 2.62. Thanks to skasal@redhat.com.

* Wed May  7 2008 Daniel Kopecek <dkopecek@redhat.com> - 1.4-0.1.20080804svn
- Initial build.

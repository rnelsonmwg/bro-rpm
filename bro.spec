%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Summary: Open-source, Unix-based Network Intrusion Detection System
Name: bro
Version: 1.5.1
Release: 10%{?dist}
License: BSD
Group: Applications/Internet
URL: http://bro-ids.org

Source0: ftp://bro-ids.org/%{name}-1.5-release.tar.gz
Source1: bro-1.5.cfg
Source2: bro.service

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libpcap-devel openssl-devel zlib-devel
BuildRequires: ncurses-devel libtool flex bison byacc
BuildRequires: file-devel bind-devel python2-devel python-tools
BuildRequires: systemd-units

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

#for triggerun
Requires(post): systemd-sysv

Patch1: bro-1.5.1-configure.patch
Patch2: bro-1.5.1-openssl.patch
Patch3: bro-1.5.1-etcfix.patch
Patch4: bro-1.5.1-broctlfix.patch
Patch5: bro-1.5.1-eth0.patch

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
%setup -q -n %{name}-%{version}
%patch1 -p1 -b .configure
%patch2 -p1 -b .openssl
%patch3 -p1 -b .etcfix
%patch4 -p1 -b .broctlfix
%patch5 -p1 -b .eth0

b="%{buildroot}"

sed -ibak "s|BRO_BINDIR|$b%{_bindir}|g"					aux/broctl/BroControl/options.py
sed -ibak "s|BRO_CFGDIR|$b%{_sysconfdir}/bro|g"				aux/broctl/BroControl/options.py
sed -ibak "s|BRO_SPOOLDIR|$b%{_localstatedir}/spool/bro|g"		aux/broctl/BroControl/options.py
sed -ibak "s|BRO_POLICYDIR|$b%{_datadir}/bro|g"				aux/broctl/BroControl/options.py
sed -ibak "s|BRO_LIBDIR|$b%{_libdir}|g"					aux/broctl/BroControl/options.py
sed -ibak "s|BRO_TMPDIR|$b%{_localstatedir}/spool/bro/tmp|g"		aux/broctl/BroControl/options.py
sed -ibak "s|BRO_TMPEXECDIR|$b%{_localstatedir}/spool/bro/tmp|g"	aux/broctl/BroControl/options.py
sed -ibak "s|BRO_STATSDIR|$b%{_localstatedir}/log/bro/stats|g"		aux/broctl/BroControl/options.py
sed -ibak "s|BRO_LOGDIR|$b%{_localstatedir}/log/bro|g"			aux/broctl/BroControl/options.py

sed -ibak "s|BROCTL_LIBDIR|$b%{_libdir}/broctl|g"				aux/broctl/BroControl/options.py
sed -ibak "s|BROCTL_TEMPLATEDIR|$b%{_datadir}/broctl/templates|g"		aux/broctl/BroControl/options.py
sed -ibak "s|BROCTL_STATICDIR|$b%{_datadir}/broctl|g"				aux/broctl/BroControl/options.py
sed -ibak "s|BROCTL_SCRIPTSDIR|$b%{_datadir}/broctl/scripts|g"			aux/broctl/BroControl/options.py
sed -ibak "s|BROCTL_POSTPROCDIR|$b%{_datadir}/broctl/scripts/postprocessors|g"	aux/broctl/BroControl/options.py
sed -ibak "s|BROCTL_HELPERDIR|$b%{_datadir}/broctl/scripts/helpers|g"		aux/broctl/BroControl/options.py

sed -ibak "s|%LIB_DIR%|%{_libdir}|g" 		aux/broctl/bin/broctl.in
sed -ibak "s|%SYSCONF_DIR%|%{_sysconfdir}|g"	aux/broctl/bin/broctl.in

%build
%configure --enable-brov6 --enable-int64

%{__make}

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
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/log/bro/stats

# Create spool dir
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/spool/bro
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/spool/bro/tmp

# Install scripts
pushd scripts
%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/scripts
%{__install} -c -m 644 bro.rc-hooks.sh  %{buildroot}%{_datadir}/bro/scripts/bro.rc-hooks.sh
%{__install} -D -c -m 644 %{SOURCE2}    %{buildroot}%{_unitdir}/bro.service

#%{__install} -c -m 755 mail_reports.sh		%{buildroot}%{_datadir}/bro/scripts/mail_reports.sh
#%{__install} -c -m 755 mail_notice.sh		%{buildroot}%{_datadir}/bro/scripts/mail_notice.sh
#%{__install} -c -m 755 bro_log_compress.sh	%{buildroot}%{_datadir}/bro/scripts/bro_log_compress.sh
popd

pushd aux/scripts
# Excluded host-grep mon-report because they require /bin/csh
for aux_script in bro-logchk.pl ca-create ca-issue host-to-addrs hot-report ip-grep lock_file mvlog; do
    %{__install} -c -m 755 ${aux_script} %{buildroot}%{_datadir}/bro/scripts/${aux_script}
done
popd

#pushd s2b
#%{__install} -d -m 755 %{buildroot}%{_datadir}/bro/scripts/s2b
#%{__install} -c -m 755 snort2bro/snort2bro      %{buildroot}%{_datadir}/bro/scripts/s2b/snort2bro
#%{__install} -c -m 644 snort2bro/snort2bro.cfg  %{buildroot}%{_datadir}/bro/scripts/s2b/snort2bro.cfg
#popd

# Install example signatures, site policy
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/site
%{__install} -D -d -m 755 %{buildroot}%{_localstatedir}/lib/bro/host
%{__install} -c -m 644 scripts/s2b/example_bro_files/signatures.sig     %{buildroot}%{_localstatedir}/lib/bro/site/signatures.sig
%{__install} -c -m 644 scripts/local.lite.bro                           %{buildroot}%{_localstatedir}/lib/bro/site/localhost.bro

# Install broctl
%{__make} DESTDIR="%{buildroot}" install-broctl

rm -rf src/libedit

# Fix paths
sed -i 's|%{buildroot}||g' %{buildroot}%{_libdir}/broctl/BroControl/options.py
sed -i 's|%{buildroot}||g' %{buildroot}%{_bindir}/broctl
sed -i 's|lib/broctl|%{_libdir}/broctl|g' %{buildroot}%{_bindir}/broctl

# Remove devel and junk files
find "%{buildroot}/%_prefix" -iname "*.la" -delete;
find "%{buildroot}/%_prefix" -iname "*.[ha]"  -delete;
find "%{buildroot}/" -iname "*.log" -delete;

%clean
rm -rf %{buildroot}

%post
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable bro.service > /dev/null 2>&1 || :
    /bin/systemctl stop bro.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart bro.service >/dev/null 2>&1 || :
fi

%triggerun -- bro < 1.5.1-5
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply bro
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save bro >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del bro >/dev/null 2>&1 || :
/bin/systemctl try-restart bro.service >/dev/null 2>&1 || :


%files
%defattr(-,root,root,-)

%doc README COPYING AUTHORS CHANGES NEWS
%doc doc/user-manual/BroDir.pdf doc/user-manual/bro-deployment.pdf
%doc doc/user-manual/Bro-user-manual.pdf doc/quick-start/bro-deployment.pdf
%doc doc/quick-start/Bro-quick-start.pdf

%config(noreplace) %{_sysconfdir}/sysconfig/bro
%config(noreplace) %{_sysconfdir}/broccoli.conf
%config(noreplace) %{_sysconfdir}/bro/broctl.cfg
%config(noreplace) %{_sysconfdir}/bro/node.cfg
%config(noreplace) %{_sysconfdir}/bro/networks.cfg
%config(noreplace) %{_sysconfdir}/bro/analysis.dat

%{_unitdir}/bro.service

%{_bindir}/bro
%{_bindir}/broctl
%{_bindir}/broccoli-config
%{_bindir}/capstats
%{_bindir}/cf
%{_bindir}/hf
%{_bindir}/trace-summary

%{_libdir}/broctl
%{_libdir}/libbroccoli.so*

%{_datadir}/bro
%{_datadir}/broctl

%{_localstatedir}/run/bro
%{_localstatedir}/log/bro
%{_localstatedir}/lib/bro
%{_localstatedir}/spool/bro

%changelog
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

%define vitver  03
%define rhver   %((head -1 /etc/redhat-release 2>/dev/null || echo 0) | tr -cd 0-9 | cut -c1)
%define relver  EC.%{vitver}%{?dist}%{!?dist:.el%{rhver}}

Name:           fuse
Version:        2.9.5
Release:        %{relver}
Summary:        File System in Userspace (FUSE) utilities

Group:          System Environment/Base
License:        GPL+
URL:            https://github.com/libfuse
Source0:        https://github.com/libfuse/libfuse/releases/download/fuse_2_9_5/%{name}-%{version}.tar.gz
Source1:        fuse-udev.nodes
Source2:        fuse-makedev.d-fuse

#Patch0:         fuse-udev_rules.patch
#Patch1:         fuse-openfix.patch
#Patch2:         fusermount.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:       kernel >= 2.6.14
Requires:       which
BuildRequires:  libselinux-devel, libtool, gettext-devel

Requires(pre): shadow-utils
Requires(post): MAKEDEV
Requires(preun): chkconfig
Requires(preun): initscripts

%description
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE userspace tools to
mount a FUSE filesystem.

%package libs
Summary:        File System in Userspace (FUSE) libraries
Group:          System Environment/Libraries
License:        LGPLv2+

%description libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE libraries.


%package devel
Summary:        File System in Userspace (FUSE) devel files
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       pkgconfig
License:        LGPLv2+

%description devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE based applications/filesystems.


%prep
%setup -q -n fuse-2.9.5
#disable device creation during build/install
sed -i 's|mknod|echo Disabled: mknod |g' util/Makefile.am
#%patch0 -p0 -b .patch0
#%patch1 -p0 -b .patch1
#%patch2 -p0 -b .patch2

%build
#touch config.rpath
#./makeconf.sh
# Can't pass --disable-static here, or else the utils don't build
#%configure \
# --libdir=/%{_lib} \
# --bindir=/bin \
# --exec-prefix=/
#make CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -j8" %{?_smp_mflags}
autoreconf --force --install
aclocal
#./configure
%configure \
 --libdir=/%{_lib} \
 --bindir=/bin \
 --exec-prefix=/
make CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" -j8

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'
# FIXME change from 60 to 99
install -D -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/makedev.d/99-fuse.nodes
install -D -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/makedev.d/z-fuse
# change from 4755 to 0755 to allow stripping -- fixed later in files
chmod 0755 $RPM_BUILD_ROOT/bin/fusermount
# Put pc file in correct place
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT%{_libdir}

# Get rid of static libs
rm -f $RPM_BUILD_ROOT/%{_lib}/*.a
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/init.d/fuse

# Compatibility symlinks
mkdir -p $RPM_BUILD_ROOT%{_bindir}
ln -s /bin/fusermount $RPM_BUILD_ROOT%{_bindir}/fusermount
ln -s /bin/ulockmgr_server $RPM_BUILD_ROOT%{_bindir}/ulockmgr_server

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/MAKEDEV fuse

%pre
getent group fuse >/dev/null || groupadd -r fuse
exit 0

%preun
# kill the deprecated fuse service if it exists
if [ -f /etc/init.d/fuse ] ; then
    /sbin/service fuse stop >/dev/null 2>&1
    /sbin/chkconfig --del fuse
fi


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING  NEWS README.NFS
/sbin/mount.fuse
%attr(4750,root,fuse) /bin/fusermount
/bin/ulockmgr_server
%config(noreplace) %{_sysconfdir}/makedev.d/z-fuse
# Compat symlinks
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%config(noreplace) %{_sysconfdir}/udev/rules.d/99-fuse.rules
%config(noreplace) %{_sysconfdir}/udev/makedev.d/99-fuse.nodes
/usr/share/man/man1/
/usr/share/man/man8/

%files libs
%defattr(-,root,root,-)
%doc COPYING.LIB
/%{_lib}/libfuse.so.*
/%{_lib}/libulockmgr.so.*

%files devel
%defattr(-,root,root,-)
/%{_lib}/libfuse.so
/%{_lib}/libulockmgr.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/fuse.h
%{_includedir}/ulockmgr.h
%{_includedir}/fuse

%changelog
* Mon Jun 06 2016 Julio Gonzalez Gil <git@juliogonzalez.es> 2.8.5-03
- Fix package building for new fuse hosting at GitHub

* Sat Apr 25 2015 Julio Gonzalez Gil <git@juliogonzalez.es> 2.8.5-02
- Include a patch to fix compilation problems
  for details see http://sourceforge.net/p/fuse/fuse/ci/655794

* Sun Jan 31 2011 Vitki <vitki@vitki.net> - 2.8.5-01
- upgrade to fuse 2.8.5 required for s3fs stability
  for details see http://code.google.com/p/s3fs/wiki/FuseOverAmazon

* Fri Apr 24 2009 Josef Bacik <josef@redhat.com> - 2.7.4-8
- use -fno-strict-aliasing in the build flags
- add a fuse group and make sure fusermount belongs to that group for security
  reasons

* Thu Apr 23 2009 Josef Bacik <josef@redhat.com> - 2.7.4-7
- fixed more post and preun stuff

* Thu Apr 23 2009 Josef Bacik <josef@redhat.com> - 2.7.4-6
- fixed some other comments related to the post and prerun stuff

* Tue Apr 21 2009 Josef Bacik <josef@redhat.com> - 2.7.4-5
- fixed some rpmlint errors

* Thu Apr 16 2009 Josef Bacik <josef@redhat.com> - 2.7.4-4
- Rebuild for RHEL5

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 28 2009 Peter Lemenkov <lemenkov@gmail.com> 2.7.4-2
- Fixed BZ#479581

* Sat Aug 23 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.4-1
- Ver. 2.7.4

* Sat Jul 12 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-3
- Fixed initscripts (BZ#441284)

* Thu Feb 28 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-2
- Fixed BZ#434881

* Wed Feb 20 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-1
- Ver. 2.7.3
- Removed usergroup fuse
- Added chkconfig support (BZ#228088)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.7.2-2
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.2-1
- bump to 2.7.2
- fix license tag

* Sun Nov  4 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-9
- fix initscript to work with chkconfig

* Mon Oct  1 2007 Peter Lemenkov <lemenkov@gmail.com> 2.7.0-8
- Added Require: which (BZ#312511)

* Fri Sep 21 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-7
- revert udev rules change

* Thu Sep 20 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-6
- change udev rules so that /dev/fuse is chmod 666 (bz 298651)

* Wed Aug 29 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-5
- fix open issue (bz 265321)

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.7.0-4
- Rebuild for selinux ppc32 issue.

* Sun Jul 22 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-3
- put pkgconfig file in correct place
- enable compat symlinks for files in /bin

* Sat Jul 21 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-2
- redefine exec_prefix to /
- redefine bindir to /bin
- redefine libdir to %%{_lib}
- don't pass --disable-static to configure
- manually rm generated static libs

* Wed Jul 18 2007 Peter Lemenkov <lemenkov@gmail.com> 2.7.0-1
- Version 2.7.0
- Redefined exec_prefix due to demands from NTFS-3G

* Wed Jun  6 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.5-2
- Add BR libselinux-devel (bug #235145)
- Config files properly marked as config (bug #211122)

* Sat May 12 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.5-1
- Version 2.6.5

* Thu Feb 22 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.3-2
- Fixed bug #229642

* Wed Feb  7 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.3-1
* Ver. 2.6.3

* Tue Dec 26 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.1-1
- Ver. 2.6.1

* Sat Nov 25 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.0-2
- fixed nasty typo (see bug #217075)

* Fri Nov  3 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.0-1
- Ver. 2.6.0

* Sun Oct 29 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-5
- Fixed udev-rule again

* Sat Oct  7 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-4
- Fixed udev-rule

* Tue Sep 12 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-3%{?dist}
- Rebuild for FC6

* Wed May 03 2006 Peter Lemenkov <lemenkov@newmail.ru> 2.5.3-1%{?dist}
- Update to 2.5.3

* Thu Mar 30 2006 Peter Lemenkov <lemenkov@newmail.ru> 2.5.2-4%{?dist}
- rebuild

* Mon Feb 13 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-3
- Proper udev rule

* Mon Feb 13 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-2
- Added missing requires

* Tue Feb 07 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-1
- Update to 2.5.2
- Dropped fuse-mount.fuse.patch

* Wed Nov 23 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.2-1
- Use dist

* Wed Nov 23 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.2-1
- Update to 2.4.2 (solves CVE-2005-3531)
- Update README.fedora

* Sat Nov 12 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-3
- Add README.fedora
- Add hint to README.fedora and that you have to be member of the group "fuse"
  in the description
- Use groupadd instead of fedora-groupadd

* Fri Nov 04 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-2
- Rename packages a bit
- use makedev.d/40-fuse.nodes
- fix /sbin/mount.fuse
- Use a fuse group to restict access to fuse-filesystems

* Fri Oct 28 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-1
- Initial RPM release.
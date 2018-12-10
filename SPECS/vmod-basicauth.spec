Name: vmod-basicauth
Summary: Basic Auth VMOD for Varnish
Version: 1.6
Release: 2%{?dist}
License: GPLv3+
Group: System Environment/Daemons
URL: http://git.gnu.org.ua/repo/vmod-basicauth.git/
Source0: http://download.gnu.org.ua/release/%{name}/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: varnish%{?_isa} = %(pkg-config --silence-errors --modversion varnishapi || echo 0)

BuildRequires: make
BuildRequires: gcc
BuildRequires: pkgconfig
BuildRequires: varnish
BuildRequires: varnish-libs-devel

# Add these when building from a git checkout
#BuildRequires: autoconf
#BuildRequires: automake
#BuildRequires: libtool
#BuildRequires: python-docutils

%description
This module implements basic HTTP authentication against the password file
created with the htpasswd(1) utility.  The following password hashes are
supported: Apache MD5, crypt(3), SHA1, and plaintext.


%prep
%setup -q


%build

# Use prebuilt manpage. Remove this when building from a git checkout
export RST2MAN=/bin/true

%configure \
  --docdir=%{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}

# We have to remove rpath - not allowed in Fedora
# (This problem only visible on 64 bit arches)
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g;
        s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%check
make check


%install
# Clean buildroot on older el variants
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# None of these for fedora/epel
find %{buildroot}/%{_libdir}/ -name '*.la' -exec rm -f {} ';'
find %{buildroot}/%{_libdir}/ -name  '*.a' -exec rm -f {} ';'
 

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_libdir}/varnish*/vmods/
%license COPYING
%doc README NEWS ChangeLog AUTHORS
%{_mandir}/man3/*.3*


%changelog
* Fri Dec 29 2017 Ingvar Hagelund <ingvar@redpill-linpro.com> - 1.6-2
- Rebuilt against varnish-5.2.1

* Thu Oct 26 2017 Ingvar Hagelund <ingvar@redpill-linpro.com> - 1.6-1
- Built newly released 1.6 against varnish-5.2.0

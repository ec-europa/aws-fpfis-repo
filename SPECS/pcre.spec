# Is this a stable/testing release:
#%%global rcversion RC1
Name:       pcre
Version:    8.41
Release:    %{?rcversion:0.}1%{?rcversion:.%rcversion}%{?dist}.2
%global myversion %{version}%{?rcversion:-%rcversion}
Summary:    Perl-compatible regular expression library
## Source package only:
# INSTALL:                  ???
# install-sh:               MIT and Public Domain
# ltmain.sh:                (GPLv2+ or BSD) and GPLv3+
# missing:                  GPLv2+ or BSD
# compile:                  GPLv2+ or BSD
# config.sub:               GPLv3+ or BSD
# m4/ax_pthread.m4:         GPLv3+ with exception
# m4/libtool.m4:            GPLv2+ or BSD
# m4/ltversion.m4:          FSFULLR
# m4/pcre_visibility.m4:    FSFULLR
# m4/lt~obsolete.m4:        FSFULLR
# m4/ltsugar.m4:            FSFULLR
# m4/ltoptions.m4:          FSFULLR
# aclocal.m4:               (GPLv2+ or BSD) and FSFULLR
# Makefile.in:              FSFULLR
# configure:                FSFUL
# test-driver:              GPLv2+ with exception
# testdata:                 Public Domain (see LICENSE file)
## Binary packages:
# other files:              BSD
License:    BSD
URL:        http://www.pcre.org/
Source:     ftp://ftp.csx.cam.ac.uk/pub/software/programming/%{name}/%{?rcversion:Testing/}%{name}-%{myversion}.tar.bz2
# Upstream thinks RPATH is a good idea.
Patch0:     pcre-8.21-multilib.patch
# Refused by upstream, bug #675477
Patch1:     pcre-8.32-refused_spelling_terminated.patch
BuildRequires:  readline-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  coreutils
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glibc-common
BuildRequires:  libtool
BuildRequires:  make
# perl not used because config.h.generic is pregenerated
# Tests:
BuildRequires:  bash
BuildRequires:  diffutils
BuildRequires:  grep

%description
PCRE, Perl-compatible regular expression, library has its own native API, but
a set of wrapper functions that are based on the POSIX API are also supplied
in the libpcreposix library. Note that this just provides a POSIX calling
interface to PCRE: the regular expressions themselves still follow Perl syntax
and semantics. This package provides support for strings in 8-bit and UTF-8
encodings. Detailed change log is provided by %{name}-doc package.

%package utf16
Summary:    UTF-16 variant of PCRE
Conflicts:  %{name}%{?_isa} < 8.38-12

%description utf16
This is Perl-compatible regular expression library working on UTF-16 strings.
Detailed change log is provided by %{name}-doc package.

%package utf32
Summary:    UTF-32 variant of PCRE
Conflicts:  %{name}%{?_isa} < 8.38-12

%description utf32
This is Perl-compatible regular expression library working on UTF-32 strings.
Detailed change log is provided by %{name}-doc package.

%package cpp
Summary:    C++ bindings for PCRE
Requires:   %{name}%{?_isa} = %{version}-%{release}

%description cpp
This is C++ bindings for the Perl-compatible regular expression library.
Detailed change log is provided by %{name}-doc package.

%package doc
Summary:    Change log for %{name}
BuildArch:  noarch

%description doc
These are large documentation files about PCRE.

%package devel
Summary:    Development files for %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}
Requires:   %{name}-cpp%{?_isa} = %{version}-%{release}
Requires:   %{name}-utf16%{?_isa} = %{version}-%{release}
Requires:   %{name}-utf32%{?_isa} = %{version}-%{release}

%description devel
Development files (Headers, libraries for dynamic linking, etc) for %{name}.

%package static
Summary:    Static library for %{name}
Requires:   %{name}-devel%{_isa} = %{version}-%{release}

%description static
Library for static linking for %{name}.

%package tools
Summary:    Auxiliary utilities for %{name}
Requires:   %{name}%{_isa} = %{version}-%{release}

%description tools
Utilities demonstrating PCRE capabilities like pcregrep or pcretest.

%prep
%setup -q -n %{name}-%{myversion}
# Get rid of rpath
%patch0 -p1
%patch1 -p1
# Because of rpath patch
libtoolize --copy --force
autoreconf -vif
# One contributor's name is non-UTF-8
for F in ChangeLog; do
    iconv -f latin1 -t utf8 "$F" >"${F}.utf8"
    touch --reference "$F" "${F}.utf8"
    mv "${F}.utf8" "$F"
done

%build
# There is a strict-aliasing problem on PPC64, bug #881232
%ifarch ppc64
%global optflags %{optflags} -fno-strict-aliasing
%endif
%configure \
%ifarch s390 s390x sparc64 sparcv9 riscv64
    --disable-jit \
%else
    --enable-jit \
%endif
    --enable-pcretest-libreadline \
    --enable-utf \
    --enable-unicode-properties \
    --enable-pcre8 \
    --enable-pcre16 \
    --enable-pcre32 \
    --disable-silent-rules
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
# Get rid of unneeded *.la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
# These are handled by %%doc in %%files
rm -rf $RPM_BUILD_ROOT%{_docdir}/pcre

%check
%ifarch s390 s390x ppc
# larger stack is needed on s390, ppc
ulimit -s 10240
%endif
make %{?_smp_mflags} check VERBOSE=yes

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post utf16 -p /sbin/ldconfig
%postun utf16 -p /sbin/ldconfig

%post utf32 -p /sbin/ldconfig
%postun utf32 -p /sbin/ldconfig

%post cpp -p /sbin/ldconfig
%postun cpp -p /sbin/ldconfig

%files
%{_libdir}/libpcre.so.*
%{_libdir}/libpcreposix.so.*
%{!?_licensedir:%global license %%doc}
%license COPYING LICENCE
%doc AUTHORS NEWS

%files utf16
%{_libdir}/libpcre16.so.*
%license COPYING LICENCE
%doc AUTHORS NEWS

%files utf32
%{_libdir}/libpcre32.so.*
%license COPYING LICENCE
%doc AUTHORS NEWS

%files cpp
%{_libdir}/libpcrecpp.so.*

%files doc
%doc ChangeLog

%files devel
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*.h
%{_mandir}/man1/pcre-config.*
%{_mandir}/man3/*
%{_bindir}/pcre-config
%doc doc/*.txt doc/html
%doc README HACKING pcredemo.c

%files static
%{_libdir}/*.a
%{!?_licensedir:%global license %%doc}
%license COPYING LICENCE

%files tools
%{_bindir}/pcregrep
%{_bindir}/pcretest
%{_mandir}/man1/pcregrep.*
%{_mandir}/man1/pcretest.*

%changelog
* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.41-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.41-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Petr Pisar <ppisar@redhat.com> - 8.41-1
- 8.41 bump

* Wed Jun 14 2017 Petr Pisar <ppisar@redhat.com> - 8.41-0.1.RC1
- 8.41 RC1 bump

* Fri Apr 21 2017 Petr Pisar <ppisar@redhat.com> - 8.40-7
- Fix a buffer overflow in pcretest tool when copying a string in UTF-32 mode
- Fix CVE-2017-7186 in JIT mode (a crash when finding a Unicode property for
  a character with a code point greater than 0x10ffff in UTF-32 library while
  UTF mode is disabled) (bug #1434504)

* Mon Mar 27 2017 Petr Pisar <ppisar@redhat.com> - 8.40-6
- Fix DFA match for a possessively repeated character class (upstream bug #2086)

* Mon Feb 27 2017 Petr Pisar <ppisar@redhat.com> - 8.40-5
- Fix a crash in pcretest when \O directive was supplied with too big number
  (upstream bug #2044)
- Document pcretest input cannot contain binary zeroes (upstream bug #2045)
- Fix CVE-2017-7244 (a crash when finding a Unicode property for a character
  with a code point greater than 0x10ffff in UTF-32 library while UTF mode is
  disabled) (upstream bug #2052)

* Thu Feb 23 2017 Petr Pisar <ppisar@redhat.com> - 8.40-4
- Fix a crash in pcretest when printing non-ASCII characters
  (upstream bug #2043)

* Tue Feb 21 2017 Petr Pisar <ppisar@redhat.com> - 8.40-3
- Fix parsing comments between quantifiers (upstream bug #2019)

* Tue Feb 14 2017 Petr Pisar <ppisar@redhat.com> - 8.40-2
- Fix pcregrep multi-line matching --only-matching option (upstream bug #1848)
- Fix CVE-2017-6004 (a crash in JIT compilation) (upstream bug #2035)
- Fix a potenial buffer overflow in formatting a pcregrep error message
  (upstream bug #2037)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.40-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Igor Gnatenko <ignatenko@redhat.com> - 8.40-1.1
- Rebuild for readline 7.x

* Thu Jan 12 2017 Petr Pisar <ppisar@redhat.com> - 8.40-1
- 8.40 bump

* Mon Dec 12 2016 Petr Pisar <ppisar@redhat.com> - 8.40-0.1.RC1
- 8.40-RC1 bump

* Mon Oct 24 2016 Petr Pisar <ppisar@redhat.com> - 8.39-6
- Document assert capture limitation (upstream bug #1887)

* Wed Oct 19 2016 Petr Pisar <ppisar@redhat.com> - 8.39-5
- Fix internal option documentation in pcrepattern(3) (upstream bug #1875)
- Fix optimization bugs for patterns starting with lookaheads
  (upstream bug #1882)

* Fri Oct 14 2016 Petr Pisar <ppisar@redhat.com> - 8.39-4
- Fix displaying position in pcretest callout with an escape sequence greater
  than \x{ff}
- Fix pcrepattern(3) documentation
- Fix miscopmilation of conditionals when a group name start with "R"
  (upstream bug #1873)

* Tue Aug 30 2016 Petr Pisar <ppisar@redhat.com> - 8.39-3
- Fix register overwite in JIT when SSE2 acceleration is enabled
- Fix matching characters above 255 when a negative character type was used
  without enabled UCP in a positive class (upstream bug #1866)

* Mon Jun 20 2016 Petr Pisar <ppisar@redhat.com> - 8.39-2
- Fix repeated pcregrep output if -o with -M options were used and the match
  extended over a line boundary (upstream bug #1848)

* Tue Jun 14 2016 Petr Pisar <ppisar@redhat.com> - 8.39-1
- 8.39 bump

* Tue May 24 2016 Petr Pisar <ppisar@redhat.com> - 8.39-0.1.RC1
- 8.39-RC1 bump

* Thu Apr 07 2016 Petr Pisar <ppisar@redhat.com> - 8.38-14
- Separate pcre-cpp subpackage for C++ bindings, thanks to Yaakov Selkowitz
  (bug #1324580)
- Correct pcre-devel dependencies
- Remove rich dependency from pcre-doc

* Mon Mar 07 2016 Petr Pisar <ppisar@redhat.com> - 8.38-13
- Remove useless dependencies between UTF variants

* Mon Mar 07 2016 Petr Pisar <ppisar@redhat.com> - 8.38-12
- Move UTF-16 and UTF-32 libraries into pcre-ut16 and pcre-32 subpackages

* Mon Mar 07 2016 Petr Pisar <ppisar@redhat.com> - 8.38-11
- Ship ChangeLog in pcre-doc package

* Sat Mar  5 2016 Peter Robinson <pbrobinson@fedoraproject.org> 8.38-10
- Don't ship ChangeLog, details covered in NEWS
- Ship README in devel as it covers API and build, not general info

* Mon Feb 29 2016 Petr Pisar <ppisar@redhat.com> - 8.38-9
- Fix a non-diagnosis of missing assection after (?(?C) that could corrupt
  process stack (upstream bug #1780)
- Fix a typo in pcre_study()

* Mon Feb 29 2016 Petr Pisar <ppisar@redhat.com> - 8.38-8
- Fix CVE-2016-1283 (a heap buffer overflow in handling of nested duplicate
  named groups with a nested back reference) (bug #1295386)
- Fix a heap buffer overflow in pcretest causing infinite loop when matching
  globally with an ovector less than 2 (bug #1312786)

* Thu Feb 11 2016 Petr Pisar <ppisar@redhat.com> - 8.38-7
- Fix pcretest for expressions with a callout inside a look-behind assertion
  (upstream bug #1783)
- Fix CVE-2016-3191 (workspace overflow for (*ACCEPT) with deeply nested
  parentheses) (upstream bug #1791)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 8.38-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec 08 2015 Petr Pisar <ppisar@redhat.com> - 8.38-6
- Fix a crash in pcre_get_substring_list() if the use of \K caused the start
  of the match to be earlier than the end (upstream bug #1744)

* Mon Dec 07 2015 Petr Pisar <ppisar@redhat.com> - 8.38-5
- Fix possible crash in pcre_copy_named_substring() if a named substring has
  number greater than the space in the ovector (upstream bug #1741)
- Fix a buffer overflow when compiling an expression with named groups with
  a group that reset capture numbers (upstream bug #1742)

* Fri Dec 04 2015 Petr Pisar <ppisar@redhat.com> - 8.38-4
- Fix compiling expressions with global extended modifier that is disabled by
  local no-extended option at the start of the expression just after
  a whitespace

* Tue Dec 01 2015 Petr Pisar <ppisar@redhat.com> - 8.38-3
- Fix compiling expressions with negated classes in UCP mode
  (upstream bug #1732)
- Fix compiling expressions with an isolated \E between an item and its
  qualifier with auto-callouts (upstream bug #1724)
- Fix crash in regexec() if REG_STARTEND option is set and pmatch argument is
  NULL (upstream bug #1727)
- Fix a stack overflow when formatting a 32-bit integer in pcregrep tool
  (upstream bug #1728)
- Fix compiling expressions with an empty \Q\E sequence between an item and
  its qualifier with auto-callouts (upstream bug #1735)

* Fri Nov 27 2015 Petr Pisar <ppisar@redhat.com> - 8.38-2
- Fix compiling comments with auto-callouts

* Tue Nov 24 2015 Petr Pisar <ppisar@redhat.com> - 8.38-1
- 8.38 bump

* Wed Nov 18 2015 Petr Pisar <ppisar@redhat.com> - 8.38-0.2.RC1
- Fix crash when compiling an expression with long (*MARK) or (*THEN) names
- Fix compiling a POSIX character class followed by a single ASCII character
  in a class item while UCP mode is active (upstream bug #1717)
- Fix mismatching characters in the range 128-255 against [:punct:] in UCP
  mode (upstream bug #1718)

* Thu Oct 29 2015 Petr Pisar <ppisar@redhat.com> - 8.38-0.1.RC1
- 8.38-RC1 bump

* Mon Oct 12 2015 Petr Pisar <ppisar@redhat.com> - 8.37-5
- Fix compiling classes with a negative escape and a property escape
  (upstream bug #1697)

* Tue Aug 25 2015 Petr Pisar <ppisar@redhat.com> - 8.37-4
- Fix CVE-2015-8381 (a heap overflow when compiling certain expression with
  named references) (bug #1256452)

* Thu Aug 06 2015 Petr Pisar <ppisar@redhat.com> - 8.37-3
- Fix a buffer overflow with duplicated named groups with a reference between
  their definition, with a group that reset capture numbers
- Fix a buffer overflow with a forward reference by name to a group whose
  number is the same as the current group
- Fix CVE-2015-8385 (a buffer overflow with duplicated named groups and an
  occurrence of "(?|") (bug #1250946)

* Wed Jul 01 2015 Petr Pisar <ppisar@redhat.com> - 8.37-2
- Fix CVE-2015-3210 (heap overflow when compiling an expression with named
  recursive back reference and the name is duplicated) (bug #1236659)
- Fix CVE-2015-5073 (heap overflow when compiling an expression with an
  forward reference within backward asserion with excessive closing
  paranthesis) (bug #1237224)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.37-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Apr 28 2015 Petr Pisar <ppisar@redhat.com> - 8.37-1
- 8.37 bump

* Thu Apr 23 2015 Petr Pisar <ppisar@redhat.com> - 8.37-0.2.RC1
- Fix static linking (bug #1214494)
- Package pcredemo.c as a documentation for pcre-devel
- Fix JIT on AArch64

* Wed Apr 22 2015 Petr Pisar <ppisar@redhat.com> - 8.37-0.1.RC1
- 8.37 RC1 bump

* Thu Apr 09 2015 Petr Pisar <ppisar@redhat.com> - 8.36-5
- Fix computing size for pattern with a negated special calss in on-UCP mode
  (bug #1210383)
- Fix compilation of a pattern with mutual recursion nested inside other group
  (bug #1210393)
- Fix compilation of a parenthesized comment (bug #1210410)
- Fix compliation of mutual recursion inside a lookbehind assertion
  (bug #1210417)
- Fix pcregrep loop when \K is used in a lookbehind assertion (bug #1210423)
- Fix pcretest loop when \K is used in a lookbehind assertion (bug #1210423)
- Fix backtracking for \C\X* in UTF-8 mode (bug #1210576)

* Thu Mar 26 2015 Petr Pisar <ppisar@redhat.com> - 8.36-4
- Fix computing size of JIT read-only data (bug #1206131)

* Thu Feb 19 2015 David Tardon <dtardon@redhat.com> - 8.36-3.1
- rebuild for C++ stdlib API changes in gcc5

* Thu Nov 20 2014 Petr Pisar <ppisar@redhat.com> - 8.36-3
- Fix CVE-2014-8964 (unused memory usage on zero-repeat assertion condition)
  (bug #1165626)

* Fri Nov 07 2014 Petr Pisar <ppisar@redhat.com> - 8.36-2
- Reset non-matched groups within capturing group up to forced match
  (bug #1161587)

* Tue Oct 07 2014 Petr Pisar <ppisar@redhat.com> - 8.36-1
- 8.36 bump

* Tue Sep 16 2014 Petr Pisar <ppisar@redhat.com> - 8.36-0.1.RC1
- 8.36 RC1 bump
- Enable JIT on aarch64

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.35-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug 11 2014 Petr Pisar <ppisar@redhat.com> - 8.35-6
- Fix compile-time loop for recursive reference within a group with an
  indefinite repeat (bug #1128577)

* Wed Jul 30 2014 Tom Callaway <spot@fedoraproject.org> - 8.35-5
- fix license handling

* Mon Jul 14 2014 Petr Pisar <ppisar@redhat.com> - 8.35-4
- Fix empty-matching possessive zero-repeat groups in interpreted mode
  (bug #1119241)
- Fix memory leaks in pcregrep (bug #1119257)
- Fix compiler crash for zero-repeated groups with a recursive back reference
  (bug #1119272)

* Thu Jun 19 2014 Petr Pisar <ppisar@redhat.com> - 8.35-3
- Fix bad starting data when char with more than one other case follows
  circumflex in multiline UTF mode (bug #1110620)
- Fix not including VT in starting characters for \s if pcre_study() is used
  (bug #1111045)
- Fix character class with a literal quotation (bug #1111054)

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.35-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 11 2014 Petr Pisar <ppisar@redhat.com> - 8.35-2
- Do no rely on wrapping signed integer while parsing {min,max} expression
  (bug #1086630)

* Wed Apr 09 2014 Petr Pisar <ppisar@redhat.com> - 8.35-1
- 8.35 bump
- Run tests in parallel

* Fri Mar 14 2014 Petr Pisar <ppisar@redhat.com> - 8.35-0.1.RC1
- 8.35-RC1 bump

* Tue Mar 11 2014 Petr Pisar <ppisar@redhat.com> - 8.34-4
- Fix max/min quantifiers in ungreedy mode (bug #1074500)

* Tue Jan 21 2014 Dan Horák <dan[at]danny.cz> - 8.34-3
- enlarge stack for tests on s390x

* Thu Jan 09 2014 Petr Pisar <ppisar@redhat.com> - 8.34-2
- Fix jitted range check (bug #1048097)

* Mon Dec 16 2013 Petr Pisar <ppisar@redhat.com> - 8.34-1
- 8.34 bump

* Wed Oct 16 2013 Petr Pisar <ppisar@redhat.com> - 8.33-3
- Disable strict-aliasing on PPC64 (bug #881232)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.33-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 03 2013 Petr Pisar <ppisar@redhat.com> - 8.33-2
- Disable unsupported JIT on aarch64 (bug #969693)

* Thu May 30 2013 Petr Pisar <ppisar@redhat.com> - 8.33-1
- 8.33 bump

* Thu May 16 2013 Petr Pisar <ppisar@redhat.com> - 8.33-0.3.RC1
- Fix passing too small output vector to pcre_dfa_exec (bug #963284)

* Mon May 13 2013 Petr Pisar <ppisar@redhat.com> - 8.33-0.2.RC1
- Fix bad handling of empty lines in pcregrep tool (bug #961789)
- Fix possible pcretest crash with a data line longer than 65536 bytes

* Thu May 02 2013 Petr Pisar <ppisar@redhat.com> - 8.33-0.1.RC1
- 8.33-RC1 bump

* Mon Jan 28 2013 Petr Pisar <ppisar@redhat.com> - 8.32-4
- Fix forward search in JIT when link size is 3 or greater
- Fix buffer over-read in UTF-16 and UTF-32 modes with JIT

* Fri Jan 25 2013 Peter Robinson <pbrobinson@fedoraproject.org> 8.32-3
- Adjust autoreconf to fix FTBFS on F-19

* Mon Jan 07 2013 Petr Pisar <ppisar@redhat.com> - 8.32-2
- Make inter-subpackage dependencies architecture specific (bug #892187)

* Fri Nov 30 2012 Petr Pisar <ppisar@redhat.com> - 8.32-1
- 8.32 bump

* Thu Nov 29 2012 Petr Pisar <ppisar@redhat.com> - 8.32-0.2.RC1
- Inter-depend sub-packages to prevent from mixing different versions

* Tue Nov 13 2012 Petr Pisar <ppisar@redhat.com> - 8.32-0.1.RC1
- 8.32-RC1 bump

* Mon Sep 03 2012 Petr Pisar <ppisar@redhat.com> - 8.31-2
- Set re_nsub in regcomp() properly (bug #853990)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.31-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Petr Pisar <ppisar@redhat.com> - 8.31-1
- 8.31 bump

* Tue Jun 05 2012 Petr Pisar <ppisar@redhat.com> - 8.31-0.1.RC1
- 8.31-RC1 bump

* Sat May 12 2012 Tom Callaway <spot@fedoraproject.org> - 8.30-7
- disable jit for sparcv9 and sparc64

* Fri May 11 2012 Petr Pisar <ppisar@redhat.com> - 8.30-6
- Fix spelling in manual pages (bug #820978)

* Mon Apr 23 2012 Petr Pisar <ppisar@redhat.com> - 8.30-5
- Possessify high ASCII (bug #815217)
- Fix ovector overflow (bug #815214)

* Fri Apr 20 2012 Petr Pisar <ppisar@redhat.com> - 8.30-4
- Possesify \s*\R (bug #813237)

* Thu Apr 05 2012 Petr Pisar <ppisar@redhat.com> - 8.30-3
- Fix look-behind assertion in UTF-8 JIT mode (bug #810314)

* Tue Feb 28 2012 Petr Pisar <ppisar@redhat.com> - 8.30-2
- Remove old libpcre.so.0 from distribution
- Move library to /usr

* Thu Feb 09 2012 Petr Pisar <ppisar@redhat.com> - 8.30-1
- 8.30 bump
- Add old libpcre.so.0 to preserve compatibility temporarily

* Fri Jan 27 2012 Petr Pisar <ppisar@redhat.com> - 8.30-0.1.RC1
- 8.30 Relase candidate 1 with UTF-16 support and *API change*
- Enable UTF-16 variant of PCRE library
- The pcre_info() function has been removed from pcre library.
- Loading compiled pattern does not fix endianity anymore. Instead an errror
  is returned and the application can use pcre_pattern_to_host_byte_order() to
  convert the pattern.
- Surrogates (0xD800---0xDFFF) are forbidden in UTF-8 mode now.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.21-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Jan 02 2012 Petr Pisar <ppisar@redhat.com> - 8.21-2
- Fix unmatched subpattern to not become wildcard (bug #769597)
- Fix NULL pointer derefernce in pcre_free_study() (upstream bug #1186)

* Mon Dec 12 2011 Petr Pisar <ppisar@redhat.com> - 8.21-1
- 8.21 bump

* Thu Dec 08 2011 Karsten Hopp <karsten@redhat.com> 8.21-0.2.RC1
- ppc needs a larger stack similar to s390

* Tue Dec 06 2011 Petr Pisar <ppisar@redhat.com> - 8.21-0.1.RC1
- 8.21-RC1 bump

* Fri Dec 02 2011 Petr Pisar <ppisar@redhat.com> - 8.20-7
- Fix case-less match if cases differ in encoding length (bug #756675)

* Fri Nov 25 2011 Petr Pisar <ppisar@redhat.com> - 8.20-6
- Fix cache-flush in JIT on PPC

* Tue Nov 22 2011 Petr Pisar <ppisar@redhat.com> - 8.20-5
- Fix repeated forward reference (bug #755969)

* Wed Nov 16 2011 Petr Pisar <ppisar@redhat.com> - 8.20-4
- Fix other look-behind regressions

* Tue Nov 15 2011 Petr Pisar <ppisar@redhat.com> - 8.20-3
- Fix look-behind regression in 8.20

* Tue Nov 15 2011 Dan Horák <dan[at]danny.cz> - 8.20-2
- fix build on s390(x) - disable jit and use larger stack for tests

* Fri Oct 21 2011 Petr Pisar <ppisar@redhat.com> - 8.20-1
- 8.20 bump

* Tue Oct 11 2011 Petr Pisar <ppisar@redhat.com> - 8.20-0.1.RC3
- 8.20-RC3 bump

* Fri Sep 23 2011 Petr Pisar <ppisar@redhat.com> - 8.20-0.1.RC2
- 8.20-RC2 bump

* Mon Sep 12 2011 Petr Pisar <ppisar@redhat.com> - 8.20-0.1.RC1
- 8.20-RC1 bump with JIT

* Tue Sep 06 2011 Petr Pisar <ppisar@redhat.com> - 8.13-4
- Fix infinite matching PRUNE (bug #735720)

* Mon Aug 22 2011 Petr Pisar <ppisar@redhat.com> - 8.13-3
- Fix parsing named class in expression (bug #732368)

* Thu Aug 18 2011 Petr Pisar <ppisar@redhat.com> - 8.13-2
- Separate utilities from libraries
- Move pcre-config(1) manual to pcre-devel sub-package
- Remove explicit defattr from spec code
- Compile pcretest with readline support

* Thu Aug 18 2011 Petr Pisar <ppisar@redhat.com> - 8.13-1
- 8.13 bump: Bug-fix version, Unicode tables updated to 6.0.0, new pcregrep
  option --buffer-size to adjust to long lines, new feature is passing of
  *MARK information to callouts.
- Should fix crash back-tracking over unicode sequence (bug #691319)

* Mon May 09 2011 Petr Pisar <ppisar@redhat.com> - 8.12-4
- Fix caseless reference matching in UTF-8 mode when the upper/lower case
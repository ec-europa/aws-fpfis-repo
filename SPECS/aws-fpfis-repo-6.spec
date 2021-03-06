Name:           aws-fpfis-repo
Version:        6
Release:        1%{?dist} 
Summary:        FPFIS Packages for Enterprise Linux repository configuration

Group:          System Environment/Base
License:        GPLv2

# This is a FPFIS maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.

URL:            https://github.com/ec-europa/aws-fpfis-repo
Source0:        aws-fpfis-repo-6.repo
Source1:        FPFIS-REPO-KEY 
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}%{version}

%description
This package contains the FPFIS Packages for Enterprise Linux (EL) repository on AWS
GPG key as well as configuration for yum.

%prep
%setup  -c -T

%build


%install
rm -rf %{buildroot} 

#GPG Key
install -Dpm 644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/pki/rpm-gpg/FPFIS-REPO-KEY

# yum
install -dm 755 %{buildroot}%{_sysconfdir}/yum.repos.d
install -pm 644 %{SOURCE0}  \
    %{buildroot}%{_sysconfdir}/yum.repos.d/aws-fpfis.repo

%clean
rm -rf %{buildroot} 

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/yum.repos.d/*
%{_sysconfdir}/pki/rpm-gpg/*

%changelog
* Wed Feb 15 2017 Rudi Van Houdt <rudi@iadept.be>
- Apapt it for AWS fpfis repo

* Tue Dec 20 2016 Gregory Boddin <gregory@siwhine.net> - 6-1
- Created package for easy install on RHELs
 
* Mon Dec 16 2013 Dennis Gilmore <dennis@ausil.us> - 6-0.1
- initial epel 6 build. 


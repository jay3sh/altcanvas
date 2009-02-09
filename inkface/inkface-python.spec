Name: inkface-python	
Version: 0.1.3	
Release: 1
Summary: inkface python bindings	

Group: System Environment/Shells
License: GPL v3
URL: http://altcanvas.googlecode.com/files/
Source0: inkface_%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires: libaltsvg
Requires: libaltsvg

%define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

%description
Solves great problems like world peace.

%prep
%setup -q

%build
scons -Q python-lib

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/
scons -Q install prefix=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{python_sitelib}/inkface.so
%defattr(-,root,root,-)
%doc


%changelog

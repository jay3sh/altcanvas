Name: libaltsvg
Version: 0.1.3	
Release: 1
Summary: libaltsvg

Group: System Environment/Shells
License: GPL v3
URL: http://altcanvas.googlecode.com/files/
Source0: libaltsvg_%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:    pkgconfig >= 0.8
Requires:         glib2 >= @GLIB_REQUIRED@
Requires:         cairo >= @CAIRO_REQUIRED@
Requires:         libxml2 >= @LIBXML_REQUIRED@
Requires:         pango >= @PANGOFT2_REQUIRED@
Requires:     libgsf >= 1.6.0
BuildRequires:    glib2-devel >= @GLIB_REQUIRED@
BuildRequires:    cairo-devel >= @CAIRO_REQUIRED@
BuildRequires:    libxml2-devel >= @LIBXML_REQUIRED@
BuildRequires:    pango-devel >= @PANGOFT2_REQUIRED@
BuildRequires:    libgsf >= 1.6.0


%description
Solves great problems like world peace.

%prep
%setup -q


%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
#mkdir -p $RPM_BUILD_ROOT/usr
#make install DESTDIR=$RPM_BUILD_ROOT

%makeinstall
mkdir -p $RPM_BUILD_ROOT/libaltsvg-%{version}

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_includedir}/libaltsvg/inkface.h
%{_includedir}/libaltsvg/rsvg.h
%{_libdir}/libaltsvg.a
%{_libdir}/libaltsvg.la
%{_libdir}/libaltsvg.so
%{_libdir}/libaltsvg.so.0
%{_libdir}/libaltsvg.so.0.1.1
%{_libdir}/pkgconfig/libaltsvg.pc
%defattr(-,root,root,-)
%doc



%changelog

%bcond_without	tests
Summary:	Kolab XML format collection parser library
Name:		libkolabxml
Version:	0.8.1
Release:	1
License:	LGPLv3+
Group:		Libraries
URL:		http://www.kolab.org
Source0:	http://mirror.kolabsys.com/pub/releases/%{name}-%{version}.tar.gz
# Source0-md5:	a02541b35153334c69ee1845dfe464c6
BuildRequires:	QtCore-devel
BuildRequires:	boost-devel
BuildRequires:	cmake >= 2.6
BuildRequires:	curl-devel
BuildRequires:	e2fsprogs-devel
BuildRequires:	kde4-kdelibs-devel
BuildRequires:	kde4-kdepimlibs-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libuuid-devel
BuildRequires:	php-devel >= 5.3
BuildRequires:	python-devel
BuildRequires:	qt4-build
BuildRequires:	swig
BuildRequires:	swig-php
BuildRequires:	xerces-c-devel
BuildRequires:	xsd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The libkolabxml parsing library interprets Kolab XML formats (xCal,
xCard) with bindings for Python, PHP and other languages. The language
bindings are available through sub-packages.

%package devel
Summary:	Kolab XML library development headers
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	QtCore-devel
Requires:	boost-devel
Requires:	cmake >= 2.6
Requires:	curl-devel
Requires:	e2fsprogs-devel
Requires:	kde4-kdelibs-devel
Requires:	kde4-kdepimlibs-devel
Requires:	libstdc++-devel
Requires:	libuuid-devel
Requires:	php-devel >= 5.3
Requires:	python-devel
Requires:	swig
Requires:	xerces-c-devel
Requires:	xsd

%description devel
Development headers for the Kolab XML libraries.

%package -n php-kolabformat
Summary:	PHP bindings for libkolabxml
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
%{?requires_php_extension}

%description -n php-kolabformat
The PHP kolabformat package offers a comprehensible PHP library using
the bindings provided through libkolabxml.

%package -n python-kolabformat
Summary:	Python bindings for libkolabxml
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description -n python-kolabformat
The PyKolab format package offers a comprehensive Python library using
the bindings provided through libkolabxml.

%prep
%setup -q

%build
install -d build
cd build
%{cmake} -Wno-fatal-errors -Wno-errors \
	-DCMAKE_SKIP_RPATH=ON \
	-DCMAKE_PREFIX_PATH=%{_libdir} \
	-DINCLUDE_INSTALL_DIR=%{_includedir}/kolabxml \
	-DPYTHON_INCLUDE_DIRS=%{python_include} \
	-DPHP_BINDINGS=ON \
	-DPHP_INSTALL_DIR=%{php_extensiondir} \
	-DPYTHON_BINDINGS=ON \
	-DPYTHON_INSTALL_DIR=%{py_sitedir} \
	..
%{__make}
cd ..

%if %{with tests}
cd build
# Make sure libkolabxml.so.* is found, otherwise the tests fail
export LD_LIBRARY_PATH=$( pwd )/src/
cd tests
./bindingstest ||:
./conversiontest ||:
./parsingtest ||:
cd ..
php -d enable_dl=On -dextension=src/php/kolabformat.so src/php/test.php ||:
python src/python/test.py ||:
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT \
	INSTALL='install -p'

install -d $RPM_BUILD_ROOT/%{_datadir}/php
mv $RPM_BUILD_ROOT/%{php_extensiondir}/kolabformat.php $RPM_BUILD_ROOT/%{php_data_dir}/kolabformat.php

install -d $RPM_BUILD_ROOT/%{php_sysconfdir}/
cat >$RPM_BUILD_ROOT/%{php_sysconfdir}/kolabformat.ini <<EOF
extension=kolabformat.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc DEVELOPMENT NEWS README
%attr(755,root,root) %{_libdir}/libkolabxml.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libkolabxml.so.0

%files devel
%defattr(644,root,root,755)
%{_includedir}/kolabxml
%{_libdir}/*.so
%{_libdir}/cmake/Libkolabxml

%files -n php-kolabformat
%defattr(644,root,root,755)
%config(noreplace) %{php_sysconfdir}/kolabformat.ini
%{php_data_dir}/kolabformat.php
%{php_extensiondir}/kolabformat.so

%files -n python-kolabformat
%defattr(644,root,root,755)
%{py_sitedir}/kolabformat.py*
%{py_sitedir}/_kolabformat.so

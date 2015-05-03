#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_without	php		# PHP bindings
%bcond_without	python		# Python bindings

%define		php_name	php55
Summary:	Kolab XML format collection parser library
Name:		libkolabxml
Version:	1.0.1
Release:	10
License:	LGPL v3+
Group:		Libraries
Source0:	http://mirror.kolabsys.com/pub/releases/%{name}-%{version}.tar.gz
# Source0-md5:	7adccfa0ed91ac954c815e8d13f334ee
URL:		http://www.kolab.org/
BuildRequires:	QtCore-devel
BuildRequires:	boost-devel
BuildRequires:	cmake >= 2.6
BuildRequires:	curl-devel
BuildRequires:	e2fsprogs-devel
BuildRequires:	kde4-kdelibs-devel
BuildRequires:	kde4-kdepimlibs-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libuuid-devel
BuildRequires:	qt4-build
BuildRequires:	rpmbuild(macros) >= 1.600
BuildRequires:	swig
BuildRequires:	xerces-c-devel
BuildRequires:	xsd
%if %{with python}
BuildRequires:	python-devel
BuildRequires:	swig-python
%endif
%if %{with php}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-program
BuildRequires:	%{php_name}-devel
BuildRequires:	swig-php
%endif
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
Requires:	swig
Requires:	xerces-c-devel
Requires:	xsd

%description devel
Development headers for the Kolab XML libraries.

%package -n %{php_name}-kolabformat
Summary:	PHP bindings for libkolabxml
Group:		Development/Languages/PHP
Requires:	%{name} = %{version}-%{release}
%{?requires_php_extension}

%description -n %{php_name}-kolabformat
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
%cmake \
	-Wno-fatal-errors -Wno-errors \
	-DCMAKE_SKIP_RPATH=ON \
	-DCMAKE_PREFIX_PATH=%{_libdir} \
	-DINCLUDE_INSTALL_DIR=%{_includedir}/kolabxml \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
%if %{with php}
	-DPHP_EXECUTABLE=%{__php} \
	-DPHP_BINDINGS=ON \
	-DPHP_INSTALL_DIR=%{php_extensiondir} \
%endif
%if %{with python}
	-DPYTHON_BINDINGS=ON \
	-DPYTHON_INCLUDE_DIRS=%{python_include} \
	-DPYTHON_INSTALL_DIR=%{py_sitedir} \
%endif
	..
%{__make}
cd ..

%if %{with tests}
cd build
# Make sure libkolabxml.so.* is found, otherwise the tests fail
export LD_LIBRARY_PATH=$(pwd)/src
cd tests
./bindingstest
./conversiontest
./parsingtest
cd ..
%if %{with php}
cd src/php
php -d 'enable_dl=On' '-dextension=../../src/php/kolabformat.so' test.php
cd ..
%endif
%if %{with python}
cd python
# FIXME
%{__python} test.py ||
cd ..
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install \
	INSTALL='install -p' \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with php}
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_data_dir}}
mv $RPM_BUILD_ROOT%{php_extensiondir}/kolabformat.php $RPM_BUILD_ROOT%{php_data_dir}/kolabformat.php
cat > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/kolabformat.ini <<EOF
; Enable kolabformat extension module
extension=kolabformat.so
EOF
%endif

%if %{with python}
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc DEVELOPMENT NEWS README
%attr(755,root,root) %{_libdir}/libkolabxml.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libkolabxml.so.1

%files devel
%defattr(644,root,root,755)
%{_includedir}/kolabxml
%{_libdir}/libkolabxml.so
%{_libdir}/cmake/Libkolabxml

%if %{with php}
%files -n %{php_name}-kolabformat
%defattr(644,root,root,755)
%config(noreplace) %{php_sysconfdir}/conf.d/kolabformat.ini
%attr(755,root,root) %{php_extensiondir}/kolabformat.so
%{php_data_dir}/kolabformat.php
%endif

%if %{with python}
%files -n python-kolabformat
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/_kolabformat.so
%{py_sitedir}/kolabformat.py[co]
%endif

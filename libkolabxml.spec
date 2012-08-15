%{!?php_inidir:%global php_inidir %{_sysconfdir}/php.d/}
%{?el5:%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)}
%{!?python_sitelib:%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch:%global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# Filter out private python and php libs. Does not work on EPEL5,
# therefor we use it conditionally
%{?filter_setup:
%filter_provides_in %{python_sitearch}/.*\.so$
%filter_provides_in %{php_extdir}/.*\.so$
%filter_setup
}

Summary:	Kolab XML format collection parser library
Name:		libkolabxml
Version:	0.8.1
Release:	0.1
License:	LGPLv3+
Group:		Libraries
URL:		http://www.kolab.org
Source0:	http://mirror.kolabsys.com/pub/releases/libkolabxml-0.8.1.tar.gz
Patch1:		%{name}-0.7.0-fix-build-without-fpermissive.patch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
%if 0%{?rhel} < 6 && 0%{?fedora} < 15
BuildRequires:	boost141-devel
%else
BuildRequires:	boost-devel
%endif
BuildRequires:	cmake >= 2.6
BuildRequires:	e2fsprogs-devel
BuildRequires:	libstdc++-devel
%if 0%{?rhel} > 6 || 0%{?fedora} >= 16
BuildRequires:	kdelibs-devel
BuildRequires:	kdepimlibs-devel
%endif
BuildRequires:	curl-devel
BuildRequires:	php-devel >= 5.3
BuildRequires:	python-devel
BuildRequires:	qt-devel >= 3
BuildRequires:	swig
BuildRequires:	uuid-devel
BuildRequires:	xerces-c-devel
BuildRequires:	xsd

# Only valid in kolabsys.com Koji
#BuildRequires:  xsd-utils

%description
The libkolabxml parsing library interprets Kolab XML formats (xCal,
xCard) with bindings for Python, PHP and other languages. The language
bindings are available through sub-packages.

%package devel
Summary:	Kolab XML library development headers
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
%if 0%{?rhel} < 6 && 0%{?fedora} < 15
Requires:	boost141-devel
%else
Requires:	boost-devel
%endif
Requires:	cmake >= 2.6
Requires:	e2fsprogs-devel
Requires:	libstdc++-devel
%if 0%{?rhel} > 6 || 0%{?fedora} >= 16
Requires:	kdelibs-devel
Requires:	kdepimlibs-devel
%endif
Requires:	curl-devel
Requires:	php-devel >= 5.3
Requires:	python-devel
Requires:	qt-devel >= 3
Requires:	swig
Requires:	uuid-devel
Requires:	xerces-c-devel
Requires:	xsd

# Only valid in kolabsys.com Koji
#Requires:       xsd-utils

%description devel
Development headers for the Kolab XML libraries.

%package -n php-kolabformat
Summary:	PHP bindings for libkolabxml
Group:		Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
%if 0%{?rhel} > 5 || 0%{?fedora} > 15
Requires:	php(api) = %{php_core_api}
Requires:	php(zend-abi) = %{php_zend_api}
%else
Requires:	php-api = %{php_apiver}
%endif

%description -n php-kolabformat
The PHP kolabformat package offers a comprehensible PHP library using
the bindings provided through libkolabxml.

%package -n python-kolabformat
Summary:	Python bindings for libkolabxml
Group:		Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description -n python-kolabformat
The PyKolab format package offers a comprehensive Python library using
the bindings provided through libkolabxml.

%prep
%setup -q
%patch1 -p1

%build
rm -rf build
mkdir -p build
pushd build
%{cmake} -Wno-fatal-errors -Wno-errors \
	-DCMAKE_SKIP_RPATH=ON \
	-DCMAKE_PREFIX_PATH=%{_libdir} \
%if 0%{?rhel} < 6 && 0%{?fedora} < 15
	-DBOOST_LIBRARYDIR=%{_libdir}/boost141 \
	-DBOOST_INCLUDEDIR=%{_includedir}/boost141 \
	-DBoost_ADDITIONAL_VERSIONS="1.41;1.41.0" \
%endif
	-DINCLUDE_INSTALL_DIR=%{_includedir}/kolabxml \
	-DPYTHON_INCLUDE_DIRS=%{python_include} \
	-DPHP_BINDINGS=ON \
	-DPHP_INSTALL_DIR=%{php_extdir} \
	-DPYTHON_BINDINGS=ON \
	-DPYTHON_INSTALL_DIR=%{py_sitedir} \
	..
%{__make}
popd

%install
rm -rf $RPM_BUILD_ROOT
pushd build
%{__make} install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'
popd

install -d $RPM_BUILD_ROOT/%{_datadir}/php
mv $RPM_BUILD_ROOT/%{php_extdir}/kolabformat.php $RPM_BUILD_ROOT/%{_datadir}/php/kolabformat.php

install -d $RPM_BUILD_ROOT/%{php_inidir}/
cat >$RPM_BUILD_ROOT/%{php_inidir}/kolabformat.ini <<EOF
extension=kolabformat.so
EOF

%check
pushd build
# Make sure libkolabxml.so.* is found, otherwise the tests fail
export LD_LIBRARY_PATH=$( pwd )/src/
pushd tests
./bindingstest ||:
./conversiontest ||:
./parsingtest ||:
popd
php -d enable_dl=On -dextension=src/php/kolabformat.so src/php/test.php ||:
python src/python/test.py ||:
popd

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc DEVELOPMENT NEWS README
%{_libdir}/*.so.*

%files devel
%defattr(644,root,root,755)
%{_includedir}/kolabxml
%{_libdir}/*.so
%{_libdir}/cmake/Libkolabxml

%files -n php-kolabformat
%defattr(644,root,root,755)
%config(noreplace) %{php_inidir}/kolabformat.ini
%{php_data_dir}/kolabformat.php
%{php_extdir}/kolabformat.so

%files -n python-kolabformat
%defattr(644,root,root,755)
%{py_sitedir}/kolabformat.py*
%{py_sitedir}/_kolabformat.so

%changelog
* Wed Jul 25 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.0-2
- Fix build on ppc64
- New upstream version

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.0-4
- Rebuilt for https:	//fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 27 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.6.0-3
- Correct dependency on php

* Tue Jun 26 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.6.0-2
- Also remove xsd-utils requirement for -devel sub-package

* Mon Jun 25 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.6.0-1
- Actual 0.6.0 release

* Sat Jun 23 2012 Christoph Wickert <wickert@kolabsys.com> - 0.6-1
- Update to 0.6 final
- Run ldconfig in %%post and %%postun
- Mark kolabformat.ini as config file
- Export LD_LIBRARY_PATH so tests can be run in %%check
- Add php dependencies to php-kolabformat package
- Make base package requirements are arch-specific
- Filter unwanted provides of php-kolabformat and python-kolabformat

* Wed Jun 20 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.6-0.4
- Some other cleanups to prevent review scrutiny from blocking
  inclusion
- Drop build requirement for xsd-utils

* Sat Jun  9 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.6-0.2
- Git snapshot release

* Wed May 23 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.5-5
- Correct use of Python keyword None
- Snapshot version with attendee cutype support

* Tue May 22 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.5-3
- Snapshot version with attendee delegation support

* Sat May 12 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.5-2
- Snapshot version with build system changes

* Wed May  9 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.4.0-3
- Fix PHP kolabformat module packaging

* Wed May  2 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.4.0-2
- New version

* Fri Apr 20 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.3.0-1
- New version

* Mon Apr  9 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.3-0.1
- First package


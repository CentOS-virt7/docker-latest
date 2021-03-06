%if 0%{?fedora}
%global with_devel 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_unit_test 0
%endif

# modifying the dockerinit binary breaks the SHA1 sum check by docker
%global __os_install_post %{_rpmconfigdir}/brp-compress

# macros for 'docker' package VR
%global docker_ver 1.9.1
%global docker_rel 40

# docker builds in a checksum of dockerinit into docker,
# so stripping the binaries breaks docker
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif
%global provider github
%global provider_tld com
%global project docker
%global repo %{project}

%global import_path %{provider}.%{provider_tld}/%{project}/%{repo}

# docker
%global git0 https://github.com/projectatomic/%{repo}
%global commit0 86bbf842e425c6567c726912852976ccfa947e75
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# d-s-s
%global git1 https://github.com/projectatomic/%{repo}-storage-setup/
%global commit1 df2af9439577cedc2c502512d887c8df10a33cbf
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})
%global dss_libdir %{_exec_prefix}/lib/%{name}-storage-setup

# docker-novolume-plugin
%global git4 https://github.com/projectatomic/%{repo}-novolume-plugin
%global commit4 7715854b5f3ccfdbf005c9e95d6e9afcaae9376a
%global shortcommit4 %(c=%{commit4}; echo ${c:0:7})

# rhel-push-plugin
%global git5 https://github.com/projectatomic/rhel-push-plugin
%global commit5 904c0ca2a285e5e7c514c2eb90f5919bc59b6f86
%global shortcommit5 %(c=%{commit5}; echo ${c:0:7})

# docker-lvm-plugin
%global git6 https://github.com/projectatomic/%{repo}-lvm-plugin
%global commit6 3253f53a791f61397fa77478904c87460a9258ca
%global shortcommit6 %(c=%{commit6}; echo ${c:0:7})

# v1.10-migrator
%global git7 https://github.com/%{repo}/v1.10-migrator
%global commit7 c417a6a022c5023c111662e8280f885f6ac259be
%global shortcommit7 %(c=%{commit7}; echo ${c:0:7})

# Version of SELinux
%if 0%{?fedora} >= 22
%global selinux_policyver 3.13.1-119
%else
%global selinux_policyver 3.13.1-23
%endif

Name: %{repo}-latest
Version: 1.10.3
Release: 22%{?dist}
Summary: Automates deployment of containerized applications
License: ASL 2.0
URL: https://%{provider}.%{provider_tld}/projectatomic/%{repo}
ExclusiveArch: x86_64
Source0: %{git0}/archive/%{commit0}/%{repo}-%{shortcommit0}.tar.gz
Source1: %{git1}/archive/%{commit1}/%{repo}-storage-setup-%{shortcommit1}.tar.gz
Source4: %{git4}/archive/%{commit4}/%{repo}-novolume-plugin-%{shortcommit4}.tar.gz
Source5: %{name}.service
Source6: %{name}.sysconfig
Source7: %{name}-storage.sysconfig
Source8: %{name}-logrotate.sh
Source9: README.%{name}-logrotate
Source10: %{name}-network.sysconfig
Source11: %{git5}/archive/%{commit5}/rhel-push-plugin-%{shortcommit5}.tar.gz
Source12: %{git6}/archive/%{commit6}/%{repo}-lvm-plugin-%{shortcommit6}.tar.gz
Source13: %{git7}/archive/%{commit7}/v1.10-migrator-%{shortcommit7}.tar.gz

BuildRequires: git
BuildRequires: glibc-static
BuildRequires: go-md2man
BuildRequires: libseccomp-devel
BuildRequires: device-mapper-devel
BuildRequires: pkgconfig(audit)
BuildRequires: btrfs-progs-devel
BuildRequires: sqlite-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: golang >= 1.4.2
Requires: device-mapper-libs >= 7:1.02.97

# RE: rhbz#1195804 - ensure min NVR for selinux-policy
Requires: selinux-policy >= %{selinux_policyver}

Requires: %{repo}-selinux >= %{docker_ver}-%{docker_rel}
Requires: %{repo}-forward-journald >= %{docker_ver}-%{docker_rel}
Requires: %{repo}-common >= %{docker_ver}-%{docker_rel}
Requires: %{repo}-rhel-push-plugin = %{version}-%{release}

# Resolves: rhbz#1045220
Requires: xz
Provides: lxc-%{name} = %{version}-%{release}

# Match with upstream name
Provides: %{name}-engine = %{version}-%{release}

# needs tar to be able to run containers
Requires: tar

# include d-s-s into main docker package and obsolete existing d-s-s rpm
# also update BRs and Rs
Requires: lvm2 >= 7:1.02.97
Requires: xfsprogs
Obsoletes: %{repo}-storage-setup <= 0.5-3


%description
Docker is an open-source engine that automates the deployment of any
application as a lightweight, portable, self-sufficient container that will
run virtually anywhere.

Docker containers can encapsulate any payload, and will run consistently on
and between virtually any server. The same container that a developer builds
and tests on a laptop will run at scale, in production*, on VMs, bare-metal
servers, OpenStack clusters, public instances, or combinations of the above.

%if 0%{?with_unit_test}
%package unit-test
Summary: %{summary} - for running unit tests

%description unit-test
%{summary} - for running unit tests
%endif

%package logrotate
Summary: cron job to run logrotate on Docker containers
Requires: %{name} = %{version}-%{release}

%description logrotate
This package installs %{summary}. logrotate is assumed to be installed on
containers for this to work, failures are silently ignored.

%package -n %{repo}-novolume-plugin
URL: %{git4}
License: MIT
Summary: Block container starts with local volumes defined
Requires: %{name} = %{version}-%{release}

%description -n %{repo}-novolume-plugin
When a volume in provisioned via the `VOLUME` instruction in a Dockerfile or
via `docker run -v volumename`, host's storage space is used. This could lead to
an unexpected out of space issue which could bring down everything.
There are situations where this is not an accepted behavior. PAAS, for
instance, can't allow their users to run their own images without the risk of
filling the entire storage space on a server. One solution to this is to deny users
from running images with volumes. This way the only storage a user gets can be limited
and PAAS can assign quota to it.

This plugin solves this issue by disallowing starting a container with
local volumes defined. In particular, the plugin will block `docker run` with:

- `--volumes-from`
- images that have `VOLUME`(s) defined
- volumes early provisioned with `docker volume` command

The only thing allowed will be just bind mounts.

%package -n %{repo}-rhel-push-plugin
License: GPLv2
Summary: Avoids pushing a RHEL-based image to docker.io registry

%description -n %{repo}-rhel-push-plugin
In order to use this plugin you must be running at least Docker 1.10 which
has support for authorization plugins.

This plugin avoids any RHEL based image to be pushed to the default docker.io
registry preventing users to violate the RH subscription agreement.

%package -n %{repo}-lvm-plugin
License: LGPLv3
Summary: Docker volume driver for lvm volumes
Requires: %{name} = %{version}-%{release}

%description -n %{repo}-lvm-plugin
Docker Volume Driver for lvm volumes.

This plugin can be used to create lvm volumes of specified size, which can 
then be bind mounted into the container using `docker run` command.

%package v1.10-migrator
License: ASL 2.0 and CC-BY-SA
Summary: Calculates SHA256 checksums for docker layer content
Requires: %{name} = %{version}-%{release}

%description v1.10-migrator
Starting from v1.10 docker uses content addressable IDs for the images and
layers instead of using generated ones. This tool calculates SHA256 checksums
for docker layer content, so that they don't need to be recalculated when the
daemon starts for the first time.

The migration usually runs on daemon startup but it can be quite slow(usually
100-200MB/s) and daemon will not be able to accept requests during
that time. You can run this tool instead while the old daemon is still
running and skip checksum calculation on startup.

%prep
%setup -q -n %{repo}-%{commit0}

# here keep the new line above otherwise autosetup fails when applying patch
cp %{SOURCE9} .

# untar d-s-s
tar zxf %{SOURCE1}
pushd %{repo}-storage-setup-%{commit1}
sed -i 's/%{repo}/%{name}/g' %{repo}-storage-setup*
sed -i 's/%{name}_devmapper_meta_dir/%{repo}_devmapper_meta_dir/g' %{repo}-storage-setup*
popd

# untar novolume-plugin
tar zxf %{SOURCE4}
pushd %{repo}-novolume-plugin-%{commit4}/systemd
sed -i 's/Before=%{repo}.service/Before=%{name}.service/g' %{repo}-novolume-plugin.service
sed -i 's/Requires=%{repo}-novolume-plugin.socket %{repo}.service/Requires=%{repo}-novolume-plugin.socket %{name}.service/g' %{repo}-novolume-plugin.service
popd

# untar rhel-push-plugin
tar zxf %{SOURCE11}
pushd rhel-push-plugin-%{commit5}/systemd
sed -i 's/Before=%{repo}.service/Before=%{name}.service/g' rhel-push-plugin.service
sed -i 's/Requires=rhel-push-plugin.socket %{repo}.service/Requires=rhel-push-plugin.socket %{name}.service/g' rhel-push-plugin.service
popd

# untar lvm-plugin
tar zxf %{SOURCE12}
pushd %{repo}-lvm-plugin-%{commit6}/vendor
mkdir src
mv g* src/
popd
pushd %{repo}-lvm-plugin-%{commit6}/systemd
sed -i 's/Before=%{repo}.service/Before=%{name}.service/g' %{repo}-lvm-plugin.service
popd

# untar v1.10-migrator
tar zxf %{SOURCE13}

%build
# set up temporary build gopath, and put our directory there
mkdir _build
pushd _build
mkdir -p src/%{provider}.%{provider_tld}/{%{repo},projectatomic}
ln -s $(dirs +1 -l) src/%{import_path}
ln -s $(dirs +1 -l)/%{repo}-novolume-plugin-%{commit4} src/%{provider}.%{provider_tld}/projectatomic/%{repo}-novolume-plugin
ln -s $(dirs +1 -l)/rhel-push-plugin-%{commit5} src/%{provider}.%{provider_tld}/projectatomic/rhel-push-plugin
ln -s $(dirs +1 -l)/%{repo}-lvm-plugin-%{commit6} src/%{provider}.%{provider_tld}/projectatomic/%{repo}-lvm-plugin
popd

export DOCKER_GITCOMMIT="%{shortcommit0}/%{version}"
export DOCKER_BUILDTAGS="selinux seccomp"
export GOPATH=$(pwd)/_build:$(pwd)/vendor:%{gopath}
export GOPATH=$GOPATH:$(pwd)/%{repo}-novolume-plugin-%{commit4}/Godeps/_workspace
export GOPATH=$GOPATH:$(pwd)/rhel-push-plugin-%{commit5}/Godeps/_workspace
export GOPATH=$GOPATH:$(pwd)/%{repo}-lvm-plugin-%{commit6}/vendor

sed -i '/LDFLAGS_STATIC/d' hack/make/.dockerinit
IAMSTATIC=false DOCKER_DEBUG=1 bash -x hack/make.sh dynbinary
man/md2man-all.sh
pushd man/man1
rename %{repo} %{name} *
popd
pushd man/man5
rename %{repo} %{name} *
popd
pushd man/man8
rename %{repo} %{name} *
popd
cp contrib/syntax/vim/LICENSE LICENSE-vim-syntax
cp contrib/syntax/vim/README.md README-vim-syntax.md
go-md2man -in %{repo}-novolume-plugin-%{commit4}/man/%{repo}-novolume-plugin.8.md -out %{repo}-novolume-plugin.8
go-md2man -in rhel-push-plugin-%{commit5}/man/rhel-push-plugin.8.md -out rhel-push-plugin.8
go-md2man -in %{repo}-lvm-plugin-%{commit6}/man/%{repo}-lvm-plugin.8.md -out %{repo}-lvm-plugin.8

pushd $(pwd)/_build/src
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/projectatomic/%{repo}-novolume-plugin
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/projectatomic/rhel-push-plugin
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/projectatomic/%{repo}-lvm-plugin
popd

# build v1.10-migrator
pushd v1.10-migrator-%{commit7}
export GOPATH=$GOPATH:$(pwd)/Godeps/_workspace
sed -i 's/godep //g' Makefile
make v1.10-migrator-local
popd

%install
# install binary
install -d %{buildroot}%{_bindir}

for x in bundles/latest; do
    if ! test -d $x/dynbinary; then
    continue
    fi
    rm $x/dynbinary/*.md5 $x/dynbinary/*.sha256
    install -p -m 755 $x/dynbinary/%{repo}-%{version}* %{buildroot}%{_bindir}/%{name}
    break
done

# install manpages
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 man/man1/%{name}*.1 %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 man/man8/%{name}*.8 %{buildroot}%{_mandir}/man8
install -d %{buildroot}%{_mandir}/man5
install -p -m 644 man/man5/Dockerfile.5 %{buildroot}%{_mandir}/man5/Dockerfile-latest.5

# install bash completion
install -dp %{buildroot}%{_datadir}/bash-completion/completions
install -p -m 644 contrib/completion/bash/%{repo} %{buildroot}%{_datadir}/bash-completion/completions/%{name}

# install fish completion
# create, install and own /usr/share/fish/vendor_completions.d until
# upstream fish provides it
install -dp %{buildroot}%{_datadir}/fish/vendor_completions.d
install -p -m 644 contrib/completion/fish/%{repo}.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/%{name}.fish

# install container logrotate cron script
install -dp %{buildroot}%{_sysconfdir}/cron.daily/
install -p -m 755 %{SOURCE8} %{buildroot}%{_sysconfdir}/cron.daily/%{name}-logrotate

# install vim syntax highlighting
install -d %{buildroot}%{_datadir}/vim/vimfiles/{doc,ftdetect,syntax}
install -p -m 644 contrib/syntax/vim/doc/%{repo}file.txt %{buildroot}%{_datadir}/vim/vimfiles/doc/%{repo}file-latest.txt
install -p -m 644 contrib/syntax/vim/ftdetect/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/ftdetect/%{repo}file-latest.vim
install -p -m 644 contrib/syntax/vim/syntax/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax/%{repo}file-latest.vim

# install zsh completion
install -d %{buildroot}%{_datadir}/zsh/site-functions
install -p -m 644 contrib/completion/zsh/_%{repo} %{buildroot}%{_datadir}/zsh/site-functions/_%{name}

# install udev rules
install -d %{buildroot}%{_udevrulesdir}
install -p contrib/udev/80-%{repo}.rules %{buildroot}%{_udevrulesdir}/80-%{name}.rules

# install storage dir
install -d %{buildroot}%{_sharedstatedir}/%{name}

# install secret patch directory
install -d -p -m 750 %{buildroot}/%{_datadir}/rhel/secrets
# rhbz#1110876 - update symlinks for subscription management
ln -s %{_sysconfdir}/pki/entitlement %{buildroot}%{_datadir}/rhel/secrets/etc-pki-entitlement
ln -s %{_sysconfdir}/rhsm %{buildroot}%{_datadir}/rhel/secrets/rhsm
ln -s %{_sysconfdir}/yum.repos.d/redhat.repo %{buildroot}%{_datadir}/rhel/secrets/rhel7.repo

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/certs.d/redhat.{com,io}
ln -s %{_sysconfdir}/rhsm/ca/redhat-uep.pem %{buildroot}%{_sysconfdir}/%{name}/certs.d/redhat.com/redhat-ca.crt
ln -s %{_sysconfdir}/rhsm/ca/redhat-uep.pem %{buildroot}%{_sysconfdir}/%{name}/certs.d/redhat.io/redhat-ca.crt

# install systemd/init scripts
install -d %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE5} %{buildroot}%{_unitdir}

# install novolume-plugin executable, unitfile, socket and man
install -d %{buildroot}/%{_libexecdir}/%{repo}
install -p -m 755 _build/src/%{repo}-novolume-plugin %{buildroot}/%{_libexecdir}/%{repo}/%{repo}-novolume-plugin
install -p -m 644 %{repo}-novolume-plugin-%{commit4}/systemd/%{repo}-novolume-plugin.s* %{buildroot}%{_unitdir}
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 %{repo}-novolume-plugin.8 %{buildroot}%{_mandir}/man8

# install rhel-push-plugin executable, unitfile, socket and man
install -d %{buildroot}%{_libexecdir}/%{repo}
install -p -m 755 _build/src/rhel-push-plugin %{buildroot}%{_libexecdir}/%{repo}/rhel-push-plugin
install -p -m 644 rhel-push-plugin-%{commit5}/systemd/rhel-push-plugin.service %{buildroot}%{_unitdir}/rhel-push-plugin.service
install -p -m 644 rhel-push-plugin-%{commit5}/systemd/rhel-push-plugin.socket %{buildroot}%{_unitdir}/rhel-push-plugin.socket
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 rhel-push-plugin.8 %{buildroot}%{_mandir}/man8

# install %%{repo}-lvm-plugin executable, unitfile, socket and man
install -d %{buildroot}/%{_libexecdir}/%{repo}
install -p -m 755 _build/src/%{repo}-lvm-plugin %{buildroot}/%{_libexecdir}/%{repo}/%{repo}-lvm-plugin
install -p -m 644 %{repo}-lvm-plugin-%{commit6}/systemd/%{repo}-lvm-plugin.s* %{buildroot}%{_unitdir}
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 %{repo}-lvm-plugin.8 %{buildroot}%{_mandir}/man8
mkdir -p %{buildroot}%{_sysconfdir}/%{repo}
install -p -m 644 %{repo}-lvm-plugin-%{commit6}%{_sysconfdir}/%{repo}/%{repo}-lvm-plugin %{buildroot}%{_sysconfdir}/%{repo}/%{repo}-lvm-plugin

# for additional args
install -d %{buildroot}%{_sysconfdir}/sysconfig/
install -p -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -p -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/sysconfig/%{name}-network
install -p -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{name}-storage

%if 0%{?with_unit_test}
install -d -m 0755 %{buildroot}%{_sharedstatedir}/%{name}-unit-test/
cp -pav VERSION Dockerfile %{buildroot}%{_sharedstatedir}/%{name}-unit-test/.
for d in */ ; do
  cp -rpav $d %{buildroot}%{_sharedstatedir}/%{name}-unit-test/
done
# remove docker.initd as it requires /sbin/runtime no packages in Fedora
rm -rf %{buildroot}%{_sharedstatedir}/%{name}-unit-test/contrib/init/openrc/%{name}.initd
%endif

%if 0%{?with_devel}
# sources
install -d -p %{buildroot}%{gopath}/src/%{import_path}
rm -rf pkg/symlink/testdata

# remove dirs that won't be installed in devel
rm -rf vendor docs _build bundles contrib/init hack project

# install sources to devel
for dir in */ ; do
    cp -rpav $dir %{buildroot}/%{gopath}/src/%{import_path}/
done
%endif

# install %%{repo} config directory
install -dp %{buildroot}%{_sysconfdir}/%{name}

# install d-s-s
pushd %{repo}-storage-setup-%{commit1}
install -d %{buildroot}%{_bindir}
install -p -m 755 %{repo}-storage-setup.sh %{buildroot}%{_bindir}/%{name}-storage-setup
install -d %{buildroot}%{_unitdir}
install -p -m 644 %{repo}-storage-setup.service %{buildroot}%{_unitdir}/%{name}-storage-setup.service
install -d %{buildroot}%{dss_libdir}
install -p -m 644 %{repo}-storage-setup.conf %{buildroot}%{dss_libdir}/%{name}-storage-setup
install -p -m 755 libdss.sh %{buildroot}%{dss_libdir}
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 %{repo}-storage-setup.1 %{buildroot}%{_mandir}/man1/%{name}-storage-setup.1
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 644 %{repo}-storage-setup-override.conf %{buildroot}%{_sysconfdir}/sysconfig/%{name}-storage-setup
popd

# install v1.10-migrator
install -d %{buildroot}%{_bindir}
install -p -m 700 v1.10-migrator-%{commit7}/v1.10-migrator-local %{buildroot}%{_bindir}

%check
[ ! -w /run/%{name}.sock ] || {
    mkdir test_dir
    pushd test_dir
    git clone https://github.com/projectatomic/%{repo}.git -b fedora-1.10.3
    pushd %{repo}
    make test
    popd
    popd
}

%post
%systemd_post %{name}

%preun
%systemd_preun %{name}

%postun
%systemd_postun_with_restart %{name}

%triggerin -n %{name}-v1.10-migrator -- %{repo} < %{version}
%{_bindir}/v1.10-migrator-local 2>/dev/null
exit 0

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE*
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md MAINTAINERS NOTICE README*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}*
%{_mandir}/man1/%{name}*.1.gz
%{_mandir}/man5/Dockerfile-latest.5.gz
%{_mandir}/man8/%{name}-daemon.8.gz
%{_bindir}/%{name}*
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-storage-setup.service
%{_datadir}/bash-completion/completions/%{name}
%dir %{_datadir}/rhel
%{_datadir}/rhel/*
%dir %{_sharedstatedir}/%{name}
%{_udevrulesdir}/80-%{name}.rules
%{_sysconfdir}/%{name}
%dir %{dss_libdir}
%{dss_libdir}/*
%{_datadir}/vim/vimfiles/doc/%{repo}file-latest.txt
%{_datadir}/vim/vimfiles/ftdetect/%{repo}file-latest.vim
%{_datadir}/vim/vimfiles/syntax/%{repo}file-latest.vim
%dir %{_datadir}/fish/vendor_completions.d/
%{_datadir}/fish/vendor_completions.d/%{name}.fish
%{_datadir}/zsh/site-functions/_%{name}

%if 0%{?with_devel}
%files devel
%license LICENSE
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md MAINTAINERS NOTICE README.md 
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%{gopath}/src/%{import_path}
%endif

%if 0%{?with_unit_test}
%files unit-test
%{_sharedstatedir}/%{name}-unit-test/
%endif

%files logrotate
%doc README.%{name}-logrotate
%{_sysconfdir}/cron.daily/%{name}-logrotate

%files -n %{repo}-novolume-plugin
%license %{repo}-novolume-plugin-%{commit4}/LICENSE
%doc %{repo}-novolume-plugin-%{commit4}/README.md
%{_mandir}/man8/%{repo}-novolume-plugin.8.gz
%{_libexecdir}/%{repo}/%{repo}-novolume-plugin
%{_unitdir}/%{repo}-novolume-plugin.*

%files -n %{repo}-rhel-push-plugin
%license rhel-push-plugin-%{commit5}/LICENSE
%doc rhel-push-plugin-%{commit5}/README.md
%{_mandir}/man8/rhel-push-plugin.8.gz
%{_libexecdir}/%{repo}/rhel-push-plugin
%{_unitdir}/rhel-push-plugin.*

%files -n %{repo}-lvm-plugin
%license %{repo}-lvm-plugin-%{commit6}/LICENSE
%doc %{repo}-lvm-plugin-%{commit6}/README.md
%config(noreplace) %{_sysconfdir}/%{repo}/%{repo}-lvm-plugin
%{_mandir}/man8/%{repo}-lvm-plugin.8.gz
%{_libexecdir}/%{repo}/%{repo}-lvm-plugin
%{_unitdir}/%{repo}-lvm-plugin.*

%files v1.10-migrator
%license v1.10-migrator-%{commit7}/LICENSE.{code,docs}
%doc v1.10-migrator-%{commit7}/{CONTRIBUTING,README}.md
%{_bindir}/v1.10-migrator-local

%changelog
* Tue May 03 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-22
- Resolves: #1328588, ship /etc/docker/docker-lvm-plugin config file
- Resolves: #1333123, include ADD_REGISTRY and BLOCK_REGISTRY variables in
sysconfig and unitfile
From: Antonio Murdaca <runcom@redhat.com>
- built docker projectatomic/rhel7-1.10.3 commit 86bbf84
- built docker-lvm-plugin commit 3253f53

* Mon May 02 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-21
- Resolves: #1328588 - ship lvm-plugin sysconfig file

* Mon May 02 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-20
- Resolves: #1331855, #1330714, #1329220 - retain docker_devmapper_meta_dir
- Release -16 included an incorrect fix

* Wed Apr 27 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-19
- Resolves: #1326374 - correct filenames in novolume and lvm plugin unitfiles

* Wed Apr 27 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-18
- use docker-selinux >= 1.9.1-38 (RE: #1331007)
- prepend novolume and lvm plugin filenames with docker-

* Tue Apr 26 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-17
- update docker dependency NVRs
- define docker_ver and docker_rel macros for 'docker' VR

* Tue Apr 26 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-16
- Resolves: #1330714 d-s-s: continue replacing docker with
docker-latest, but retain docker_devmapper_data_dir

* Tue Apr 26 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-15
- Resolves: #1330714 d-s-s: replace docker with docker_latest, not docker-latest

* Tue Apr 26 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-14
- docker unitfile requires rhel-push-plugin.socket
- requires docker-common >= 1.9.1-36
- append docker instead of docker-latest to plugin subpackages
- Resolves: #1326374 - plugin executables installed in /usr/libexecdir/docker
- Resolves: #1330714 - d-s-s: do not pass devices which have 'creation of
device node' in progress.
- built d-s-s commit#df2af94

* Mon Apr 25 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-13
- Resolves: #1330366 - require docker-common
- rhel-push-plugin fixes From: Antonio Murdaca <runcom@redhat.com>
- built docker @projectatomic/docker commit#7fd4fb0
- built d-s-s commit#04a3847
- built novolume-plugin commit#7715854
- built rhel-push-plugin commit#904c0ca
- built docker-lvm-plugin commit#7eb53d5
- built v1.10-migrator commit#c417a6a

* Fri Apr 22 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-12
- Resolves: #1329728 - CVE-2016-3697
- built docker @projectatomic/docker commit#7fd4fb0
- built d-s-s commit#04a3847
- built novolume-plugin commit#7715854
- built rhel-push-plugin commit#2e19b59
- built docker-lvm-plugin commit#7eb53d5
- built v1.10-migrator commit#c417a6a

* Wed Apr 20 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-11
- define selinux_policyver, seemed to have skipped out earlier

* Thu Apr 14 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-10
- Resolves: rhbz#1326374 - s/docker/docker-latest where relevant
- Resolves: rhbz#1327314 - include rhel-push-plugin subpackage
- Resolves: rhbz#1327405 - include docker-lvm-plugin subpackage
- built docker-latest @projectatomic/rhel7-1.10.3 commit#5738d87
- built d-s-s commit#04a3847
- built novolume-plugin commit#7715854
- built rhel-push-plugin commit#2e19b59
- built docker-lvm-plugin commit#7eb53d5
- built v1.10-migrator commit#c417a6a

* Mon Apr 11 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-9
- built docker-latest @projectatomic/rhel7-1.10.3 commit#36da459
- built d-s-s commit#ac50cee
- built novolume-plugin commit#7715854

* Mon Apr 11 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-8
- logrotate and novolume-plugin should require docker-latest and not docker

* Mon Apr 11 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1.10.3-7
- built docker-latest @projectatomic/rhel7-1.10.3 commit#36da459
- built d-s-s commit#ac50cee
- built novolume-plugin commit#7715854

* Fri Apr 08 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.10.3-6.gitf8a9a2a
- remove selinux, forward-journald, utils and v1.10-migrator subpacakges
- use selinux, utils and forward-journald subpackages from 'docker' package
- Epoch not needed in RHEL, removed

* Thu Apr 07 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.10.3-5.gitf8a9a2a
- 'docker-latest' package for v1.10.3

* Tue Mar 29 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.10.3-4.gitf8a9a2a
- built docker @projectatomic/fedora-1.10.3 commit#f8a9a2a
- built docker-selinux commit#2bc84ec
- built d-s-s commit#f087cb1
- built docker-utils commit#b851c03
- built forward-journald commit#77e02a9

* Wed Mar 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.3-3.gitd93ee51
- built docker @projectatomic/fedora-1.10.3 commit#d93ee51
- built d-s-s commit#1c2b95b
- built docker-selinux commit#afc876c
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#77a55c1
- built docker-v1.10-migrator commit#994c35

* Wed Mar 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.3-2.gitc3689c7
- built docker @projectatomic/fedora-1.10.3 commit#c3689c7
- built d-s-s commit#1c2b95b
- built docker-selinux commit#afc876c
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#77a55c1
- built docker-v1.10-migrator commit#994c35

* Fri Mar 11 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.3-1.gite949a81
- built docker @projectatomic/fedora-1.10.3 commit#e949a81
- built d-s-s commit#1c2b95b
- built docker-selinux commit#afc876c
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#77a55c1
- built docker-v1.10-migrator commit#994c35

* Thu Mar 10 2016 Lokesh Mandvekar <lsm5fedoraproject.org> - 1:1.10.2-12.gitddbb15a
- Tmp Resolves: rhbz#1315903 - disable ppc64 build

* Mon Mar 07 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-11.gitddbb15a
- built docker @projectatomic/fedora-1.10.2 commit#ddbb15a
- built d-s-s commit#1c2b95b
- built docker-selinux commit#afc876c
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#77a55c1
- built docker-v1.10-migrator commit#994c35

* Thu Mar 03 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-10.gitddbb15a
- built docker @projectatomic/fedora-1.10.2 commit#ddbb15a
- built d-s-s commit#1c2b95b
- built docker-selinux commit#afc876c
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Wed Mar 02 2016 jchaloup <jchaloup@redhat.com> 1:1.10.2-9.git0f5ac89
- Update list of provided packages in devel subpackage

* Tue Mar  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 1:1.10.2-8.git0f5ac89
- Power64 and s390(x) now have libseccomp support

* Fri Feb 26 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-7.git0f5ac89
- rebuilt to remove dockerroot user creation

* Tue Feb 23 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-6.git0f5ac89
- rebuilt to include dss_libdir directory

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-5.git0f5ac89
- built docker @projectatomic/fedora-1.10.2 commit#0f5ac89
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-4.git86e59a5
- rebuilt to include /usr/share/rhel/secrets for the secret patch we're carrying

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.10.2-3.git86e59a5
- https://fedoraproject.org/wiki/Changes/golang1.6

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-2.git86e59a5
- rebuilt with Recommends: oci-register-machine

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-1.git86e59a5
- built docker @projectatomic/fedora-1.10.2 commit#86e59a5
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Thu Feb 18 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-8.git6c71d8f
- remove journald duplicated tag

* Thu Feb 18 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-7.git6c71d8f
- BuildRequires libseccomp-static to compile
- Requires libseccomp

* Thu Feb 18 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-6.git6c71d8f
- enable seccomp

* Tue Feb 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-5.git6c71d8f
- built docker @projectatomic/fedora-1.10.1 commit#6c71d8f
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Tue Feb 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-4.git6c71d8f
- built docker @projectatomic/fedora-1.10.1 commit#6c71d8f
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#2103b9e
- built docker-v1.10-migrator commit#994c35

* Fri Feb 12 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-3.git49805e4
- built docker @projectatomic/fedora-1.10.1 commit#49805e4
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#d1a7f4a
- built docker-v1.10-migrator commit#994c35

* Fri Feb 12 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-2.git9c1310f
- built docker @projectatomic/fedora-1.10.1 commit#9c1310f
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#d1a7f4a
- built docker-v1.10-migrator commit#994c35

* Thu Feb 11 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-1.git1b79038
- built docker @projectatomic/fedora-1.10.1 commit#1b79038
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#d1a7f4a
- built docker-v1.10-migrator commit#994c35

* Thu Feb 11 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.0-29.git1b79038
- built docker @projectatomic/fedora-1.10.1 commit#1b79038
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#04307f5b
- built docker-v1.10-migrator commit#994c35

* Sat Feb 06 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.0-28.gitf392451
- built docker @projectatomic/fedora-1.10 commit#f392451
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#60b3a94
- built docker-v1.10-migrator commit#994c35

* Fri Feb 05 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.0-27.gitf392451
- built docker @projectatomic/fedora-1.10 commit#f392451
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#1c2b95b
- built docker-v1.10-migrator commit#994c35c

* Fri Feb 05 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.0-26.gitf2e80b0
- built docker @projectatomic/fedora-1.10 commit#f2e80b0
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#1c2b95b
- built docker-v1.10-migrator commit#994c35c

* Thu Feb 04 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-24.gitd25c9e5
- built docker @projectatomic/fedora-1.10 commit#d25c9e5
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#1c2b95b
- built docker-v1.10-migrator commit#994c35c

* Thu Feb 04 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.0-24.gitd25c9e5
- built docker @projectatomic/fedora-1.10 commit#d25c9e5
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#dab51ac

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.10.0-23.gitfb1a123
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Feb 03 2016 Antonio Murdaca <runcom@redhat.com> - 1:1.10.0-22.gitfb1a123
- built docker @projectatomic/fedora-1.10 commit#fb1a123
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#dab51ac

* Mon Feb 01 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-21.gitd3f4a34
- built docker @projectatomic/fedora-1.10 commit#d3f4a34
- built docker-selinux commit#be16da7
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#dab51ac

* Fri Jan 29 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-20.gitd3f4a34
- Resolves: rhbz#1303105 - own /usr/lib/docker-storage-setup
- create docker-novolume-plugin subpackage
- built docker @projectatomic/fedora-1.10 commit#d3f4a34
- built docker-selinux commit#be16da7
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#dab51ac

* Wed Jan 27 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-19.gitb8b1153
- built docker @projectatomic/fedora-1.10 commit#b8b1153
- built docker-selinux commit#d9b67f9
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Mon Jan 25 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-18.git314b2a0
- Resolves: rhbz#1301198 - do not append distro tag to docker version
- built docker @projectatomic/fedora-1.10 commit#314b2a0
- built docker-selinux commit#d9b67f9
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Fri Jan 22 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-17.git5587979
- built docker @projectatomic/fedora-1.10 commit#5587979
- built docker-selinux commit#d9b67f9
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Wed Jan 20 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-16.git9252953
- built docker @projectatomic/fedora-1.10 commit#9252953
- built docker-selinux commit#d9b67f9
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Mon Jan 11 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-15.gite38a363
- built docker @projectatomic/fedora-1.10 commit#e38a363
- built docker-selinux commit#d9b67f9
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Thu Jan 07 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-14.gite38a363
- built docker @projectatomic/fedora-1.10 commit#e38a363
- built docker-selinux commit#d9b67f9
- built d-s-s commit#5bda7f8
- built docker-utils commit#dab51ac

* Thu Jan 07 2016 jchaloup <jchaloup@redhat.com> - 1:1.10.0-13.gitc3726aa
- built with debug info
  resolves: #1236317

* Thu Dec 10 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-12.gitc3726aa
- built docker @projectatomic/fedora-1.10 commit#c3726aa
- built docker-selinux commit#d9b67f9
- built d-s-s commit#f399708
- built docker-utils commit#dab51ac

* Wed Dec 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-11.gitc3726aa
- built docker @projectatomic/fedora-1.10 commit#c3726aa
- built docker-selinux commit#d9b67f9
- built d-s-s commit#e193b3b
- built docker-utils commit#dab51ac

* Tue Dec 08 2015 Colin Walters <walters@redhat.com>- 1:1.10.0-10.git6d8d26a
- Use new standardized source format
- Resolves: https://bugzilla.redhat.com/1284150

* Wed Dec 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-9.git6d8d26a
- built docker @projectatomic/fedora-1.10 commit#6d8d26a
- built docker-selinux commit#d9b67f9
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Tue Dec 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-8.gita7f4806
- use CAS for images and layers, upstream gh pr#17924
- built docker @projectatomic/fedora-1.10 commit#a7f4806
- built docker-selinux commit#d9b67f9
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Mon Nov 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-7.git42850f5
- built docker @projectatomic/fedora-1.10 commit#42850f5
- built docker-selinux commit#e522191
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Mon Nov 23 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-6.git39f99b6
- built docker @projectatomic/fedora-1.10 commit#39f99b6
- built docker-selinux commit#e522191
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Fri Nov 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-5.git0a9a759
- built docker @projectatomic/fedora-1.10 commit#0a9a759
- built docker-selinux commit#e522191
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Thu Nov 19 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-4.git8b9d2a6
- built docker @projectatomic/fedora-1.10 commit#8b9d2a6
- built docker-selinux commit#e522191
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Thu Nov 19 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-3.git8b9d2a6
- built docker @projectatomic/fedora-1.10 commit#8b9d2a6
- built docker-selinux commit#e522191
- built d-s-s commit#c638a60
- built docker-utils commit#dab51ac

* Mon Nov 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.0-2.git6669c1a
- built docker @projectatomic/fedora-1.10 commit#6669c1a
- built docker-selinux commit#e522191
- built d-s-s commit#c638a60
- built docker-utils commit#dab51ac

* Mon Nov 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-15.git6669c1a
- built docker @projectatomic/fedora-1.10 commit#6669c1a
- built docker-selinux commit#e522191
- built d-s-s commit#c638a60
- built docker-utils commit#dab51ac

* Fri Nov 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-14.gite08c5ef
- built docker @projectatomic/fedora-1.10 commit#e08c5ef
- built docker-selinux commit#e522191
- built d-s-s commit#e9722cc
- built docker-utils commit#dab51ac

* Fri Nov 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-13.gite08c5ef
- built docker @projectatomic/fedora-1.10 commit#e08c5ef
- built docker-selinux commit#e522191
- built d-s-s commit#e9722cc
- built docker-utils commit#dab51ac

* Thu Nov 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-12.git1c1e196
- Resolves: rhbz#1273893
- From: Dan Walsh <dwalsh@redhat.com>

* Thu Nov 12 2015 Jakub Čajka <jcajka@fedoraproject.org> - 1:1.9.0-11.git1c1e196
- clean up macros overrides

* Wed Nov 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-10.git1c1e196
- built docker @projectatomic/fedora-1.9 commit#1c1e196
- built docker-selinux commit#e522191
- Dependency changes
- For docker: Requires: docker-selinux
- For docker-selinux: Requires(post): docker
- From: Dusty Mabe <dustymabe@redhat.com>

* Tue Oct 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-9.gitc743657
- built docker @projectatomic/fedora-1.9 commit#c743657
- built docker-selinux master commit#291bbab
- built d-s-s master commit#01df512
- built docker-utils master commit#dab51ac

* Wed Oct 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-8.git6024859
- built docker @projectatomic/fedora-1.9 commit#6024859
- built docker-selinux master commit#44abd21
- built d-s-s master commit#6898d43
- built docker-utils master commit#dab51ac

* Mon Sep 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-7.git9107cd3
- build docker @rhatdan/fedora-1.9 commit#9107cd3
- built docker-selinux master commit#d6560f8

* Thu Sep 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-6.git05653f9
- built docker @rhatdan/fedora-1.9 commit#05653f9
- Resolves: rhbz#1264193, rhbz#1260392, rhbz#1264196

* Thu Sep 10 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-5.git11b81f9
- built docker @rhatdan/fedora-1.9 commit#11b81f9
- built d-s-s master commit#6898d43
- built docker-selinux master commit#b5281b7

* Wed Sep 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-4.git566d2be
- Resolves: rhbz#1259427

* Mon Aug 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-3.git566d2be
- built docker @rhatdan/ commit#566d2be
- built d-s-s master commit#d3b9ba7
- built docker-selinux master commit#6267b83
- built docker-utils master commit#dab51ac

* Fri Aug 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-2.gitf8950e0
- built docker @rhatdan/fedora-1.9 commit#f8950e0
- built d-s-s master commit#ac1b30e
- built docker-selinux master commit#16ebd81
- built docker-utils master commit#dab51ac

* Thu Aug 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.0-1
- built docker @rhatdan/fedora-1.9 commit#b4e2cc5
- built d-s-s master commit#ac1b30e
- built docker-selinux master commit#16ebd81
- built docker-utils master commit#dab51ac

* Thu Aug 06 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.0-11.git59a228f
- built docker @lsm5/fedora commit#59a228f

* Mon Aug 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.0-10.gitba026e3
- built docker @rhatdan/fedora-1.8 commit#ba026e3
- built d-s-s master commit#b152398
- built docker-selinux master commit#16ebd81

* Mon Aug 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.0-9.gitc7eed6c
- built docker @lsm5/fedora commit#c7eed6c

* Thu Jul 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.0-8.git2df828d
- built docker @rhatdan/fedora-1.8 commit#2df828d
- built d-s-s master commit#b152398
- built docker-selinux master commit#16ebd81

* Tue Jul 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-7.git5062080
- include epoch for downgrading purposes

* Fri Jul 24 2015 Tomas Radej <tradej@redhat.com> - 1.8.0-6.git5062080
- Updated dep on policycoreutils-python-utils

* Fri Jul 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-6.git5062080
- package provides: docker-engine

* Thu Jul 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-6.git5062080
- built docker @lsm5/fedora-1.8 commit#6c23e87
- enable non-x86_64 builds again

* Tue Jun 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-5.git6d5bfe5
- built docker @lsm5/fedora-1.8 commit#6d5bfe5
- make test-unit and make test-docker-py successful

* Mon Jun 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-4.git0d8fd7c
- build docker @lsm5/fedora-1.8 commit#0d8fd7c
- disable non-x86_64 for this build
- use same distro as host for running tests
- docker.service Wants docker-storage-setup.service

* Mon Jun 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-3.gita2f1a81
- built docker @lsm5/fedora commit#a2f1a81

* Sat Jun 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-2.git1cad29d
- built docker @lsm5/fedora commit#1cad29d

* Fri Jun 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-1
- New version: 1.8.0, built docker         @lsm5/commit#96ebfd2

* Fri Jun 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-21.gitdcff4e1
- build dss master commit#90f4a5f
- build docker-selinux master commit#bebf349
- update manpage build script path

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-20.gitdcff4e1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 15 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-19.gitdcff4e1
- Remove docker.initd as it requires /sbin/runtime no packages in Fedora

* Fri Jun 12 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-18.gitdcff4e1
- Add docker-unit-test subpackage for CI testing
- Add with_devel and with_unit_test macros
- Remove devel's runtime deps on golang

* Tue Jun 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-17.gitdcff4e1
- Include d-s-s into the main docker package
- Obsolete docker-storage-setup <= 0.5-3

* Mon Jun 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-16.gitdcff4e1
- Resolves: rhbz#1229433 - update docker-selinux to commit#99c4c7

* Mon Jun 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-15.gitdcff4e1
- disable debuginfo because it breaks docker

* Sun Jun 07 2015 Dennis Gilmore <dennis@ausil.us> - 1.7.0-14.gitdcff4e1
- enable %%{ix86}
- remove vishvananda/netns/netns_linux_amd.go file if %%{ix86} architecture is used

* Fri Jun 05 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-13.gitdcff4e1
- built docker @lsm5/fedora commit#dcff4e1

* Thu Jun 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-12.git9910a0c
- built docker @lsm5/fedora commit#9910a0c

* Tue Jun 02 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-11.gita53a6e6
- remove vishvananda/netns/netns_linux_amd.go file if arm architecture is used
- add debug info

* Mon Jun 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-10.gita53a6e6
- built docker @lsm5/fedora commit#a53a6e6

* Sat May 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-9.git49d9a3f
- built docker @lsm5/fedora commit#49d9a3f

* Fri May 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-8.git0d35ceb
- built docker @lsm5/fedora commit#0d35ceb

* Thu May 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-7.git6d76e4c
- built docker @rhatdan/fedora-1.7 commit#6d76e4c
- built docker-selinux master commit#e86b2bc

* Fri May 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-6.git56481a3
- include distro tag in VERSION

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-5.git56481a3
- include docker-selinux for centos7 and rhel7

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-4.git56481a3
- increment release tag to sync with docker-master on centos7

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-3.git56481a3
- built docker @lsm5/fedora commit#56481a3

* Mon Apr 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-2.git50ef691
- built docker @lsm5/fedora commit#50ef691

* Mon Apr 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-1
- New version: 1.7.0, built docker         @lsm5/commit#50ef691

* Sat Apr 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-33.git1dcc59a
- built docker @lsm5/fedora commit#1dcc59a

* Thu Apr 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-32.gitf7125f9
- built docker @lsm5/fedora commit#f7125f9

* Wed Apr 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-31.git7091837
- built docker @lsm5/fedora commit#7091837

* Wed Apr 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-30.gitece2f2d
- built docker @lsm5/fedora commit#ece2f2d

* Mon Mar 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-29.gitc9c16a3
- built docker @lsm5/fedora commit#c9c16a3

* Mon Mar 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-28.git39c97c2
- built docker @lsm5/fedora commit#39c97c2

* Sun Mar 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-27.git937f8fc
- built docker @lsm5/fedora commit#937f8fc

* Sat Mar 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-26.gitbbc21e4
- built docker @lsm5/fedora commit#bbc21e4

* Tue Mar 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-25.git5ebfacd
- move selinux post/postun to its own subpackage
- correct docker-selinux min nvr for docker main package

* Tue Mar 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-24.git5ebfacd
- docker-selinux shouldn't require docker
- move docker-selinux's post and postun to docker's

* Sun Mar 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-23.git5ebfacd
- increment release tag as -22 was already built without conditionals for f23
and docker-selinux
- Source7 only for f23+

* Sun Mar 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-22.git5ebfacd
- Rename package to 'docker', metaprovide: docker-io*
- Obsolete docker-io release 21
- no separate version tag for docker-selinux
- docker-selinux only for f23+

* Fri Mar 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-21.git5ebfacd
- selinux specific rpm code from Lukas Vrabec <lvrabec@redhat.com>
- use spaces instead of tabs

* Tue Mar 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-20.git5ebfacd
- built commit#5ebfacd

* Mon Mar 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-19.git5d7adce
- built commit#5d7adce

* Thu Mar 05 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-18.git92e632c
- built commit#92e632c

* Wed Mar 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-17.git0f6704f
- built commit#0f6704f

* Tue Mar 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-16.git8e107a9
- built commit#8e107a9

* Sun Mar 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-15.gita61716e
- built commit#a61716e

* Sat Feb 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-14.gitb52a2cf
- built commit#b52a2cf

* Fri Feb 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-13.gitf5850e8
- built commit#f5850e8

* Thu Feb 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-12.git7e2328b
- built commit#7e2328b

* Wed Feb 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-11.git09b785f
- remove add-X-flag.patch
- require selinux-policy >= 3.13.1-114 for fedora >= 23 (RE: rhbz#1195804)

* Mon Feb 23 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-10.git09b785f
- Resolves: rhbz#1195328 - solve build failures by adding -X flag back
also see (https://github.com/docker/docker/issues/9207#issuecomment-75578730)

* Wed Feb 18 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-9.git09b785f
- built commit#09b785f

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-8.git2243e32
- re-add detailed provides in -devel package
NOTE: (only providing the root path doesn't help in building packages like
kubernetes)

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-7.git2243e32
- built commit#2243e32

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-6.git2243e32
- built commit#2243e32

* Sun Feb 15 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-5.git028968f
- built commit#028968f

* Sat Feb 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-4.git9456a25
- built commit#9456a25

* Thu Feb 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-3.git802802b
- built commit#802802b

* Wed Feb 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-2.git54b59c2
- provide golang paths only upto the repo's root dir
- merge pkg-devel into devel

* Wed Feb 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-1
- New version: 1.5.0, built commit#54b59c2

* Tue Feb 10 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-27.git76baa35
- daily rebuild - Tue Feb 10 01:19:10 CET 2015

* Mon Feb 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-26.gitc03d6f5
- add config variable for insecure registry

* Sat Feb 07 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-25.gitc03d6f5
- daily rebuild - Sat Feb  7 02:53:34 UTC 2015

* Fri Feb 06 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-24.git68b0ed5
- daily rebuild - Fri Feb  6 04:27:54 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-23.git7cc9858
- daily rebuild - Wed Feb  4 22:08:05 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-22.git165ea5c
- daily rebuild - Wed Feb  4 03:10:41 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-21.git165ea5c
- daily rebuild - Wed Feb  4 03:09:20 UTC 2015

* Tue Feb 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-20.git662dffe
- Resolves: rhbz#1184266 - enable debugging
- Resolves: rhbz#1190748 - enable core dumps with no size limit

* Tue Feb 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-19.git662dffe
- daily rebuild - Tue Feb  3 04:56:36 UTC 2015

* Mon Feb 02 2015 Dennis Gilmore <dennis@ausil.us> 1.4.1-18.git9273040
- enable building on %%{arm}

* Mon Feb 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-17.git9273040
- daily rebuild - Mon Feb  2 00:08:17 UTC 2015

* Sun Feb 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-16.git01864d3
- daily rebuild - Sun Feb  1 00:00:57 UTC 2015

* Sat Jan 31 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-15.gitd400ac7
- daily rebuild - Sat Jan 31 05:08:46 UTC 2015

* Sat Jan 31 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-14.gitd400ac7
- daily rebuild - Sat Jan 31 05:07:37 UTC 2015

* Thu Jan 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-13.gitd400ac7
- daily rebuild - Thu Jan 29 14:13:04 UTC 2015

* Wed Jan 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-12.gitde52a19
- daily rebuild - Wed Jan 28 02:17:47 UTC 2015

* Tue Jan 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-11.gitacb8e08
- daily rebuild - Tue Jan 27 02:37:34 UTC 2015

* Sun Jan 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-10.gitb1f2fde
- daily rebuild - Sun Jan 25 21:44:48 UTC 2015

* Sun Jan 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-9
- use vendored sources (not built)

* Fri Jan 23 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-8
- Resolves:rhbz#1185423 - MountFlags=slave in unitfile
- use golang(github.com/coreos/go-systemd/activation)

* Fri Jan 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-7
- docker group no longer used or created
- no socket activation
- config file updates to include info about docker_transition_unconfined
boolean

* Fri Jan 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-6
- run tests inside a docker repo (doesn't affect koji builds - not built)

* Tue Jan 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-5
- Resolves: rhbz#1169593 patch to set DOCKER_CERT_PATH regardless of config file

* Thu Jan 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-4
- allow unitfile to use /etc/sysconfig/docker-network
- MountFlags private

* Fri Dec 19 2014 Dan Walsh <dwalsh@redhat.com> - 1.4.1-3
- Add check to run unit tests

* Thu Dec 18 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-2
- update and rename logrotate cron script
- install /etc/sysconfig/docker-network

* Wed Dec 17 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-1
- Resolves: rhbz#1175144 - update to upstream v1.4.1
- Resolves: rhbz#1175097, rhbz#1127570 - subpackages
for fish and zsh completion and vim syntax highlighting
- Provide subpackage to run logrotate on running containers as a daily cron
job

* Thu Dec 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.0-2
- update metaprovides

* Thu Dec 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.0-1
- Resolves: rhbz#1173324
- Resolves: rhbz#1172761 - CVE-2014-9356
- Resolves: rhbz#1172782 - CVE-2014-9357
- Resolves: rhbz#1172787 - CVE-2014-9358
- update to upstream v1.4.0
- override DOCKER_CERT_PATH in sysconfig instead of patching the source
- create dockerroot user if doesn't exist prior

* Tue Dec 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-6.gitbb24f99
- use /etc/docker instead of /.docker
- use upstream master commit bb24f99d741cd8d6a8b882afc929c15c633c39cb
- include DOCKER_TMPDIR variable in /etc/sysconfig/docker

* Mon Dec 08 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-5
- Revert to using upstream release 1.3.2

* Tue Dec 02 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-4.git353ff40
- Resolves: rhbz#1169151, rhbz#1169334

* Sun Nov 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-3.git353ff40
- Resolves: rhbz#1169035, rhbz#1169151
- bring back golang deps (except libcontainer)

* Tue Nov 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-2
- install sources skipped prior

* Tue Nov 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-1
- Resolves: rhbz#1167642 - Update to upstream v1.3.2
- Resolves: rhbz#1167505, rhbz#1167507 - CVE-2014-6407
- Resolves: rhbz#1167506 - CVE-2014-6408
- use vendor/ dir for golang deps for this NVR (fix deps soon after)

* Wed Nov 19 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-3
- Resolves: rhbz#1165615

* Fri Oct 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-2
- Remove pandoc from build reqs

* Fri Oct 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-1
- update to v1.3.1

* Mon Oct 20 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.0-1
- Resolves: rhbz#1153936 - update to v1.3.0
- don't install zsh files
- iptables=false => ip-masq=false

* Wed Oct 08 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-5
- Resolves: rhbz#1149882 - systemd unit and socket file updates

* Tue Sep 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-4
- Resolves: rhbz#1139415 - correct path for bash completion
    /usr/share/bash-completion/completions
- versioned provides for docker
- golang versioned requirements for devel and pkg-devel
- remove macros from changelog
- don't own dirs owned by vim, systemd, bash

* Thu Sep 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-3
- Resolves: rhbz#1145660 - support /etc/sysconfig/docker-storage 
  From: Colin Walters <walters@redhat.com>
- patch to ignore selinux if it's disabled
  https://github.com/docker/docker/commit/9e2eb0f1cc3c4ef000e139f1d85a20f0e00971e6
  From: Dan Walsh <dwalsh@redhat.com>

* Sun Aug 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-2
- Provides docker only for f21 and above

* Sat Aug 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-1
- Resolves: rhbz#1132824 - update to v1.2.0

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.2-2
- change conditionals

* Thu Jul 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.2-1
- Resolves: rhbz#1124036 - update to upstream v1.1.2

* Mon Jul 28 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.0.0-10
- split out the import_path/pkg/... libraries, to avoid cyclic deps with libcontainer

* Thu Jul 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-9
- /etc/sysconfig/docker should be config(noreplace)

* Wed Jul 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-8
- Resolves: rhbz#1119849
- Resolves: rhbz#1119413 - min delta between upstream and packaged unitfiles
- devel package owns directories it creates
- ensure min NVRs used for systemd contain fixes RE: CVE-2014-3499

* Wed Jul 16 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.0.0-7
- clean up gopath
- add Provides for docker libraries
- produce a -devel with docker source libraries
- accomodate golang rpm macros

* Tue Jul 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-6
- Resolves: rhbz#1114810 - CVE-2014-3499 (correct bz#)

* Tue Jul 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-5
- Resolves: rhbz#11114810 - CVE-2014-3499

* Tue Jun 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-4
- Set mode,user,group in docker.socket file

* Sat Jun 14 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-3
- correct bogus date

* Sat Jun 14 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-2
- RHBZ#1109533 patch libcontainer for finalize namespace error
- RHBZ#1109039 build with updated golang-github-syndtr-gocapability
- install Dockerfile.5 manpage

* Mon Jun 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-1
- upstream version bump to v1.0.0

* Mon Jun 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.12.0-1
- RHBZ#1105789 Upstream bump to 0.12.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 05 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-11
- unitfile should Require socket file (revert change in release 10)

* Fri May 30 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-10
- do not require docker.socket in unitfile

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-9
- BZ: change systemd service type to 'notify'

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-8
- use systemd socket-activation version

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-7
- add "Provides: docker" as per FPC exception (Matthew Miller
        <mattdm@fedoraproject.org>)

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-6
- don't use docker.sysconfig meant for sysvinit (just to avoid confusion)

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-5
- Bug 1084232 - add /etc/sysconfig/docker for additional args

* Tue May 27 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-4
- patches for BZ 1088125, 1096375

* Fri May 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-3
- add selinux buildtag
- enable selinux in unitfile

* Fri May 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-2
- get rid of conditionals, separate out spec for each branch

* Thu May 08 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-1
- Bug 1095616 - upstream bump to 0.11.1
- manpages via pandoc

* Mon Apr 14 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.10.0-2
- regenerate btrfs removal patch
- update commit value

* Mon Apr 14 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.10.0-1
- include manpages from contrib

* Wed Apr 09 2014 Bobby Powers <bobbypowers@gmail.com> - 0.10.0-1
- Upstream version bump

* Thu Mar 27 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.1-1
- BZ 1080799 - upstream version bump

* Thu Mar 13 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.9.0-3
- Add lxc requirement for EPEL6 and patch init script to use lxc driver
- Remove tar dep, no longer needed
- Require libcgroup only for EPEL6

* Tue Mar 11 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.0-2
- lxc removed (optional)
  http://blog.docker.io/2014/03/docker-0-9-introducing-execution-drivers-and-libcontainer/

* Tue Mar 11 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.0-1
- BZ 1074880 - upstream version bump to v0.9.0

* Wed Feb 19 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.1-1
- Bug 1066841 - upstream version bump to v0.8.1
- use sysvinit files from upstream contrib
- BR golang >= 1.2-7

* Thu Feb 13 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.8.0-3
- Remove unneeded sysctl settings in initscript
  https://github.com/dotcloud/docker/pull/4125

* Sat Feb 08 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.0-2
- ignore btrfs for rhel7 and clones for now
- include vim syntax highlighting from contrib/syntax/vim

* Wed Feb 05 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.0-1
- upstream version bump
- don't use btrfs for rhel6 and clones (yet)

* Mon Jan 20 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.6-2
- bridge-utils only for rhel < 7
- discard freespace when image is removed

* Thu Jan 16 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.6-1
- upstream version bump v0.7.6
- built with golang >= 1.2

* Thu Jan 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.5-1
- upstream version bump to 0.7.5

* Thu Jan 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.4-1
- upstream version bump to 0.7.4 (BZ #1049793)
- udev rules file from upstream contrib
- unit file firewalld not used, description changes

* Mon Jan 06 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-3
- udev rules typo fixed (BZ 1048775)

* Sat Jan 04 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-2
- missed commit value in release 1, updated now
- upstream release monitoring (BZ 1048441)

* Sat Jan 04 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-1
- upstream release bump to v0.7.3

* Thu Dec 19 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.2-2
- require xz to work with ubuntu images (BZ #1045220)

* Wed Dec 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.2-1
- upstream release bump to v0.7.2

* Fri Dec 06 2013 Vincent Batts <vbatts@redhat.com> - 0.7.1-1
- upstream release of v0.7.1

* Mon Dec 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-14
- sysvinit patch corrected (epel only)
- 80-docker.rules unified for udisks1 and udisks2

* Mon Dec 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-13
- removed firewall-cmd --add-masquerade

* Sat Nov 30 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-12
- systemd for fedora >= 18
- firewalld in unit file changed from Requires to Wants
- firewall-cmd --add-masquerade after docker daemon start in unit file
  (Michal Fojtik <mfojtik@redhat.com>), continue if not present (Michael Young
  <m.a.young@durham.ac.uk>)
- 80-docker.rules included for epel too, ENV variables need to be changed for
  udisks1

* Fri Nov 29 2013 Marek Goldmann <mgoldman@redhat.com> - 0.7.0-11
- Redirect docker log to /var/log/docker (epel only)
- Removed the '-b none' parameter from sysconfig, it's unnecessary since
  we create the bridge now automatically (epel only)
- Make sure we have the cgconfig service started before we start docker,
    RHBZ#1034919 (epel only)

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-10
- udev rules added for fedora >= 19 BZ 1034095
- epel testing pending

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-9
- requires and started after firewalld

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-8
- iptables-fix patch corrected

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-7
- use upstream tarball and patch with mgoldman's commit

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-6
- using mgoldman's shortcommit value 0ff9bc1 for package (BZ #1033606)
- https://github.com/dotcloud/docker/pull/2907

* Wed Nov 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 0.7.0-5
- Fix up EL6 preun/postun to not fail on postun scripts

* Wed Nov 27 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-4
- brctl patch for rhel <= 7

* Wed Nov 27 2013 Vincent Batts <vbatts@redhat.com> - 0.7.0-3
- Patch how the bridge network is set up on RHEL (BZ #1035436)

* Wed Nov 27 2013 Vincent Batts <vbatts@redhat.com> - 0.7.0-2
- add libcgroup require (BZ #1034919)

* Tue Nov 26 2013 Marek Goldmann <mgoldman@redhat.com> - 0.7.0-1
- Upstream release 0.7.0
- Using upstream script to build the binary

* Mon Nov 25 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.20.rc7
- correct the build time defines (bz#1026545). Thanks dan-fedora.

* Fri Nov 22 2013 Adam Miller <maxamillion@fedoraproject.org> - 0.7-0.19.rc7
- Remove xinetd entry, added sysvinit

* Fri Nov 22 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.18.rc7
- rc version bump

* Wed Nov 20 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.17.rc6
- removed ExecStartPost lines from docker.service (BZ #1026045)
- dockerinit listed in files

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.16.rc6
- adding back the none bridge patch

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.15.rc6
- update docker source to crosbymichael/0.7.0-rc6
- bridge-patch is not needed on this branch

* Tue Nov 19 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.14.rc5
- update docker source to crosbymichael/0.7-rc5
- update docker source to 457375ea370a2da0df301d35b1aaa8f5964dabfe
- static magic
- place dockerinit in a libexec
- add sqlite dependency

* Sat Nov 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.13.dm
- docker.service file sets iptables rules to allow container networking, this
    is a stopgap approach, relevant pull request here:
    https://github.com/dotcloud/docker/pull/2527

* Sat Oct 26 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.12.dm
- dm branch
- dockerinit -> docker-init

* Tue Oct 22 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.11.rc4
- passing version information for docker build BZ #1017186

* Sat Oct 19 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.10.rc4
- rc version bump
- docker-init -> dockerinit
- zsh completion script installed to /usr/share/zsh/site-functions

* Fri Oct 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.9.rc3
- lxc-docker version matches package version

* Fri Oct 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.8.rc3
- double quotes removed from buildrequires as per existing golang rules

* Fri Oct 11 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.7.rc3
- xinetd file renamed to docker.xinetd for clarity

* Thu Oct 10 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.6.rc3
- patched for el6 to use sphinx-1.0-build

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.5.rc3
- rc3 version bump
- exclusivearch x86_64

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.4.rc2
- debuginfo not Go-ready yet, skipped

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.3.rc2
- debuginfo package generated
- buildrequires listed with versions where needed
- conditionals changed to reflect systemd or not
- docker commit value not needed
- versioned provides lxc-docker

* Mon Oct 07 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-2.rc2
- rc branch includes devmapper
- el6 BZ #1015865 fix included

* Sun Oct 06 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-1
- version bump, includes devicemapper
- epel conditionals included
- buildrequires sqlite-devel

* Fri Oct 04 2013 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.6.3-4.devicemapper
- docker-io service enables IPv4 and IPv6 forwarding
- docker user not needed
- golang not supported on ppc64, docker-io excluded too

* Thu Oct 03 2013 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.6.3-3.devicemapper
- Docker rebuilt with latest kr/pty, first run issue solved

* Fri Sep 27 2013 Marek Goldmann <mgoldman@redhat.com> - 0.6.3-2.devicemapper
- Remove setfcap from lxc.cap.drop to make setxattr() calls working in the
  containers, RHBZ#1012952

* Thu Sep 26 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.3-1.devicemapper
- version bump
- new version solves docker push issues

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-14.devicemapper
- package requires lxc

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-13.devicemapper
- package requires tar

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-12.devicemapper
- /var/lib/docker installed
- package also provides lxc-docker

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-11.devicemapper
- better looking url

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-10.devicemapper
- release tag changed to denote devicemapper patch

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-9
- device-mapper-devel is a buildrequires for alex's code
- docker.service listed as a separate source file

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-8
- install bash completion
- use -v for go build to show progress

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-7
- build and install separate docker-init

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-4
- update to use new source-only golang lib packages

* Sat Sep 21 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-3
- man page generation from docs/.
- systemd service file created
- dotcloud/tar no longer required

* Fri Sep 20 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-2
- patched with alex larsson's devmapper code

* Wed Sep 18 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-1
- Version bump

* Tue Sep 10 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.1-2
- buildrequires updated
- package renamed to docker-io

* Fri Aug 30 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.1-1
- Version bump
- Package name change from lxc-docker to docker
- Makefile patched from 0.5.3

* Wed Aug 28 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-5
- File permissions settings included

* Wed Aug 28 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-4
- Credits in changelog modified as per reference's request

* Tue Aug 27 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-3
- Dependencies listed as rpm packages instead of tars
- Install section added

* Mon Aug 26 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-2
- Github packaging
- Deps not downloaded at build time courtesy Elan Ruusamäe
- Manpage and other docs installed

* Fri Aug 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-1
- Initial fedora package
- Some credit to Elan Ruusamäe (glen@pld-linux.org)

%define _default_patch_fuzz 2

# GNU libidn support for i18n'ed domain names
# no effect for now, mutt expects old version of libidn
%define enable_idn	0
%{?_with_idn:	%global enable_idn 1}

# compile against kerberos
%define enable_krb5	0
%{?_with_kerberos:	%global enable_krb5 1}
# enable sasl2
# note that sasl2 includes kerberos support via sasl
%define enable_sasl2	1

Summary:	Text mode mail user agent
Name:		mutt
Epoch:		1
Version:	1.5.21
Release:	13
License:	GPLv2
Group:		Networking/Mail
Url:		http://www.mutt.org/
Source0:	ftp://ftp.mutt.org/pub/mutt/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.mutt.org/pub/mutt/%{name}-%{version}.tar.gz.asc
# To make use of bzip2/gzip files
Source10:	%{name}-Muttrc_compressed_folders.foot.bz2
#
# NOTE:	For any patch that modifies Muttrc, please modify Muttrc.head.in
# instead, because Muttrc is automatically generated, so any change will
# be lost
#

#
# Patch 1-99:	Mandriva patches
#

# Set tmpdir to ~/tmp in sample config
Patch1:		%{name}-1.3.15-tmpdef.patch

# Tell user to install urlview instead of just barf at user
Patch2:		%{name}-1.5.18-urlview.patch

# Allow non root users to install mutt
Patch3:		%{name}-1.5.5.1-no-sgid.patch

# Don't include /usr/include/ncurses if not building against normal ncurses
Patch4:		%{name}-1.5.5.1-ncurses-include.patch

# fixes the viewing of MIME attached files when the mailcap
# entry already uses quotes (eg:	"%s")
Patch5:		mutt-1.5.11-mailcap.patch

# defines gpg paths, aspell, and fallback charsets
Patch6:		mutt-1.5.20-gpg.patch

# stack is not defined under openssl 1.0.0 (http://dev.mutt.org/hg/mutt/rev/1cf34ea1f128)
#Patch7:	mutt-1.5.20-stack.patch

Patch8:		mutt-1.5.21-db51.patch

#
# Patch 100- :	external patches
#

# Compressed folder support, http://www.spinnaker.de/mutt/compressed/
# http://www.mutt.org.ua/download/mutt-%{pversion}/patch-%{pversion}.rr.compressed.gz
Patch100:	patch-1.5.20.rr.compressed

# NNTP support
# http://www.mutt.org.ua/download/mutt-%{version}/patch-%{version}.vvv.nntp.gz
Patch101:	patch-1.5.20.vvv.nntp

# Dynamically set xterm window title / icon name
Patch104:	%{name}-1.5.5.1-xterm-title.patch

# Merged upstream
#Patch107:	mutt-1.5.19-nulcert.diff

# Now maintained at http://www.lunar-linux.org/index.php?option=com_content&task=view&id=44
# Patch adapted from:	patch-1.5.20.sidebar.20090619.txt
Patch108:	mutt-1.5.20-sidebar.patch

# Patch adapted from:	http://greek0.net/mutt.html
Patch109:	mutt-1.5.12-indexcolor-3+cb.diff

Patch110:	mutt-1.5.21-CVE-2011-1429.diff

BuildRequires:	sendmail-command
BuildRequires:	bzip2-devel
# required by the header cache patch
BuildRequires:	db-devel >= 5.2
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(openssl)
%if %enable_krb5
BuildRequires:	krb5-devel
%endif
%if %enable_sasl2
BuildRequires:	sasl-devel >= 2.1
%endif
# without it we have problems with attachments (e.g. .pdfs)
Suggests:	mailcap
Suggests:	mutt-utf8

%description
Mutt is a text mode mail user agent. Mutt supports color, threading,
arbitrary key remapping, and a lot of customization.

You should install mutt if you've used mutt in the past and you prefer
it, or if you're new to mail programs and you haven't decided which
one you're going to use.

%package	utf8
Summary:	Text mode mail user agent supporting wide character
Group:		Networking/Mail
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description	utf8
Mutt is a text mode mail user agent. Mutt supports color, threading,
arbitrary key remapping, and a lot of customization.

You should install mutt if you've used mutt in the past and you prefer
it, or if you're new to mail programs and you haven't decided which
one you're going to use.

NOTE:	This version of mutt is linked against ncurses with wide char
      support, and is useful for, say, people using UTF-8 locales.

%package	doc
Summary:	Manual for Mutt, a text mode mail user agent
Group:		Networking/Mail

%description	doc
This is the complete manual for Mutt, in text and HTML formats.

Mutt is a text mode mail user agent. Mutt supports color, threading,
arbitrary key remapping, and a lot of customization.

You should install mutt if you've used mutt in the past and you prefer
it, or if you're new to mail programs and you haven't decided which
one you're going to use.


%prep
%setup -q
%patch1 -p1 -b .tmpdef
%patch2 -p1 -b .urlview
%patch3 -p0 -b .no-sgid
%patch5 -p1 -b .mailcap
%patch6 -p0 -b .gpg
%patch8 -p0 -b .db5
%patch100 -p1 -b .cfp
%patch101 -p1 -b .nntp
%patch104 -p1 -b .xterm-title
%patch108 -p1
%patch109 -p1
%patch110 -p0 -b .CVE-2011-1429

sed -i 's/AM_C_PROTOTYPES//g' configure.ac
sed -i -e 's/AM_CONFIG_HEADER/AC_CONFIG_HEADERS/g' configure.ac
autoreconf -fi

# Append changes to Muttrc to make use of bzip2/gzip mbox
bzip2 -cd %{SOURCE10} >> Muttrc.head.in

# Fix some bad references in the man pages
# Reference to imapd is not fixed, since uw-imap/courier/cyrus all have
# different paths
perl -pi -e 's|/usr/local/bin|%{_bindir}|g; s|/usr/local/doc/mutt|%{_docdir}/%{name}|g;' doc/*.man init.h

%build

build()
{
	CONFIGURE_TOP=.. %configure2_5x \
	--with-docdir=%{_docdir}/%{name} \
	--enable-smtp		\
	--enable-pop		\
	--enable-imap		\
	--enable-nfs-fix	\
	--with-ssl		\
	--enable-compressed	\
	--enable-hcache		\
	--without-gdbm		\
	--with-bdb		\
	--enable-pgp		\
	--enable-smime		\
	--with-gpgme-prefix=%{_prefix} \
%if %enable_krb5
	--with-gss 		\
%else
	--without-gss 		\
%endif
%if %enable_sasl2
	--with-sasl 		\
%else
	--without-sasl	 	\
%endif
	$@ 			\
	--enable-nntp

	# no parallel make
	make
}

# build normal version
### ugly. ugly.
perl -pi -e 's/ncurses ncursesw/ncurses # ncursesw/' configure
mkdir mutt-normal
pushd mutt-normal
build
popd

# build another version enabling wide char support
### ugly. ugly.
perl -pi -e 's/ncurses # ncursesw/ncurses ncursesw/' configure
mkdir mutt-utf-8
pushd mutt-utf-8
build

# "make install" installs $builddir/Muttrc into $buildroot
make update-doc
#mv -f Muttrc ../Muttrc

popd

%install
pushd mutt-utf-8
%makeinstall_std
mv %{buildroot}%{_bindir}/mutt %{buildroot}%{_bindir}/mutt-utf8
popd

pushd mutt-normal
install -m 755 mutt %{buildroot}%{_bindir}/mutt-normal
popd

# get rid of unpackaged files
rm -f %{buildroot}%{_sysconfdir}/mime.types
mv -f %{buildroot}%{_sysconfdir}/mime.types.dist .
mv -f %{buildroot}%{_sysconfdir}/Muttrc.dist .

%find_lang %{name}

%post
update-alternatives --install %{_bindir}/mutt mutt %{_bindir}/mutt-normal 10

%preun
if [ $1 -eq 0 ]; then
  update-alternatives --remove mutt %{_bindir}/mutt-normal
fi

%post utf8
update-alternatives --install %{_bindir}/mutt mutt %{_bindir}/mutt-utf8 20

%preun utf8
if [ $1 -eq 0 ]; then
  update-alternatives --remove mutt %{_bindir}/mutt-utf8
fi

%triggerpostun -- %{name} < %{epoch}:1.5
update-alternatives --install %{_bindir}/mutt mutt %{_bindir}/mutt-normal 10

%files -f %{name}.lang
%doc BEWARE COPYRIGHT NEWS OPS* PATCHES*
%doc README* TODO UPDATING VERSION
%doc mime.types.dist Muttrc.dist
%config(noreplace) %{_sysconfdir}/Muttrc
%{_bindir}/flea
%{_bindir}/mutt-normal
%{_bindir}/muttbug
%{_bindir}/pgpewrap
%{_bindir}/pgpring
%{_bindir}/smime_keys
%attr(2755, root, mail) %{_bindir}/mutt_dotlock
%{_mandir}/man?/*

%files utf8
%{_bindir}/mutt-utf8

%files doc
%doc doc/manual.txt
%doc doc/advancedusage.html doc/gettingstarted.html doc/tuning.html
%doc doc/intro.html doc/mimesupport.html doc/reference.html
%doc doc/configuration.html doc/index.html doc/miscellany.html


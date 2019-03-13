%define _default_patch_fuzz 2

# compile against kerberos
%define enable_krb5	0
%{?_with_kerberos:	%global enable_krb5 1}
# enable sasl2
# note that sasl2 includes kerberos support via sasl
%define enable_sasl2	1

Summary:	Text mode mail user agent
Name:		mutt
Version:	1.11.4
Release:	1
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

Patch3:		mutt-1.9.2-no-sgid.patch

# fixes the viewing of MIME attached files when the mailcap
# entry already uses quotes (eg:	"%s")
Patch5:		mutt-1.5.11-mailcap.patch

# defines gpg paths, aspell, and fallback charsets
Patch6:		mutt-1.5.20-gpg.patch

Patch8:		mutt-1.5.23-db61.patch
#
# Patch 100- :	external patches
#

# Patches from http://www.mutt.org.ua/download/
Patch100:	https://www.mutt.org.ua/download/mutt-1.11.1/patch-1.11.1.vvv.initials.xz
Patch101:	https://www.mutt.org.ua/download/mutt-1.11.1/patch-1.11.1.vvv.nntp.xz
Patch102:	https://www.mutt.org.ua/download/mutt-1.11.1/patch-1.11.1.vvv.nntp_ru.xz
Patch103:	https://www.mutt.org.ua/download/mutt-1.11.1/patch-1.11.1.vvv.quote.xz

Patch110:	mutt-1.5.23-CVE-2014-9116.patch

BuildRequires:	sendmail-command
BuildRequires:	bzip2-devel
BuildRequires:	gpgme-devel
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
BuildRequires:	xsltproc
BuildRequires:	lynx
BuildRequires:	docbook-style-xsl
# without it we have problems with attachments (e.g. .pdfs)
Suggests:	mailcap
%rename %{name}-utf8

%description
Mutt is a text mode mail user agent. Mutt supports color, threading,
arbitrary key remapping, and a lot of customization.

You should install mutt if you've used mutt in the past and you prefer
it, or if you're new to mail programs and you haven't decided which
one you're going to use.

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
%autosetup -p1
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
%configure \
	--with-docdir=%{_docdir}/%{name} \
	--enable-gpgme		\
	--enable-sidebar	\
	--enable-smtp		\
	--enable-pop		\
	--enable-imap		\
	--enable-nfs-fix	\
	--with-ssl		\
	--with-idn2		\
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
%make

# "make install" installs $builddir/Muttrc into $buildroot
%make update-doc
#mv -f Muttrc ../Muttrc

%install
%make_install

# get rid of unpackaged files
rm -f %{buildroot}%{_sysconfdir}/mime.types
mv -f %{buildroot}%{_sysconfdir}/mime.types.dist .
mv -f %{buildroot}%{_sysconfdir}/Muttrc.dist .

%find_lang %{name}

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%exclude %{_docdir}/%{name}/samples
%exclude %{_docdir}/%{name}/*.html
%exclude %{_docdir}/%{name}/manual.txt

%config(noreplace) %{_sysconfdir}/Muttrc
%{_bindir}/flea
%{_bindir}/muttbug
%{_bindir}/mutt
%{_bindir}/mutt_pgpring
%{_bindir}/pgpewrap
%{_bindir}/smime_keys
%attr(2755, root, mail) %{_bindir}/mutt_dotlock
%{_mandir}/man?/*
%{_infodir}/mutt.info*

%files doc
%doc %{_docdir}/%{name}/samples 
%doc %{_docdir}/%{name}/*.html 
%doc %{_docdir}/%{name}/manual.txt

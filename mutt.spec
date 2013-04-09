%define rel			6
%define release		%mkrel %rel

%define _default_patch_fuzz 2

# GNU libidn support for i18n'ed domain names
# no effect for now, mutt expects old version of libidn
%define enable_idn	0
%{?_with_idn: %global enable_idn 1}

# compile against kerberos
%define enable_krb5	0
%{?_with_kerberos: %global enable_krb5 1}
# enable sasl2
# note that sasl2 includes kerberos support via sasl
%define enable_sasl2	1

Name:		mutt
Version:	1.5.21
Release:	%{release}
Epoch:		1

Summary:	Text mode mail user agent
License:	GPL
Group:		Networking/Mail
Url:		http://www.mutt.org/
Source0:	ftp://ftp.mutt.org/pub/mutt/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.mutt.org/pub/mutt/%{name}-%{version}.tar.gz.asc
# To make use of bzip2/gzip files
Source10:	%{name}-Muttrc_compressed_folders.foot.bz2

#
# NOTE: For any patch that modifies Muttrc, please modify Muttrc.head.in
# instead, because Muttrc is automatically generated, so any change will
# be lost
#

#
# Patch 1-99: Mandriva patches
#

# Set tmpdir to ~/tmp in sample config
Patch1:		%{name}-1.3.15-tmpdef.patch

# Tell user to install urlview instead of just barf at user
Patch2:         %{name}-1.5.18-urlview.patch

# Allow non root users to install mutt
Patch3:		%{name}-1.5.5.1-no-sgid.patch

# Don't include /usr/include/ncurses if not building against normal ncurses
Patch4:		%{name}-1.5.5.1-ncurses-include.patch

# fixes the viewing of MIME attached files when the mailcap
# entry already uses quotes (eg: "%s")
Patch5:		mutt-1.5.11-mailcap.patch

# defines gpg paths, aspell, and fallback charsets
Patch6:		mutt-1.5.20-gpg.patch

# stack is not defined under openssl 1.0.0 (http://dev.mutt.org/hg/mutt/rev/1cf34ea1f128)
#Patch7:		mutt-1.5.20-stack.patch

Patch8:		mutt-1.5.21-db51.patch

#
# Patch 100- : external patches
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
# Patch adapted from: patch-1.5.20.sidebar.20090619.txt
Patch108:	mutt-1.5.20-sidebar.patch

# Patch adapted from: http://greek0.net/mutt.html
Patch109:	mutt-1.5.12-indexcolor-3+cb.diff

Patch110:	mutt-1.5.21-CVE-2011-1429.diff

BuildRequires:	bzip2-devel
BuildRequires:	linuxdoc-tools
BuildRequires:  pkgconfig(ncursesw)
BuildRequires:  pkgconfig(ncurses)
BuildRequires:	openssl-devel
BuildRequires:	sendmail-command
# the new nntp patch can now use these versions
BuildRequires:	autoconf2.5 automake1.8
# required by the header cache patch
BuildRequires:  db-devel >= 5.2
%if %enable_krb5
BuildRequires:	krb5-devel
%endif
%if %enable_sasl2
BuildRequires:	sasl-devel >= 2.1
%endif

Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}

# without it we have problems with attachments (e.g. .pdfs)
Suggests: mailcap
Suggests: mutt-utf8


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

NOTE: This version of mutt is linked against ncurses with wide char
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
rm -rf %{buildroot}

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

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc BEWARE COPYRIGHT NEWS OPS* PATCHES*
%doc README* TODO UPDATING VERSION
%doc mime.types.dist Muttrc.dist
%config(noreplace) %{_sysconfdir}/Muttrc
%{_mandir}/man?/*
%{_bindir}/flea
%{_bindir}/mutt-normal
%{_bindir}/muttbug
%{_bindir}/pgpewrap
%{_bindir}/pgpring
%{_bindir}/smime_keys
%attr(2755, root, mail) %{_bindir}/mutt_dotlock

%files utf8
%defattr(-,root,root)
%{_bindir}/mutt-utf8

%files doc
%defattr(-,root,root)
%doc doc/manual.txt
%doc doc/advancedusage.html doc/gettingstarted.html doc/tuning.html
%doc doc/intro.html doc/mimesupport.html doc/reference.html
%doc doc/configuration.html doc/index.html doc/miscellany.html


%changelog
* Mon Apr 02 2012 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.21-4.1
- P110: security fix for CVE-2011-1429 (upstream)

* Mon Apr 11 2011 Funda Wang <fwang@mandriva.org> 1:1.5.21-4mdv2011.0
+ Revision: 652449
- build with db5.1

* Fri Apr 01 2011 RÃ©my Clouard <shikamaru@mandriva.org> 1:1.5.21-3
+ Revision: 649679
- Fix sidebar patch: readd sidebar_sort

* Thu Dec 23 2010 Lev Givon <lev@mandriva.org> 1:1.5.21-2mdv2011.0
+ Revision: 624136
- Fix misaligned Security line on composition screen.

* Sun Oct 31 2010 RÃ©my Clouard <shikamaru@mandriva.org> 1:1.5.21-1mdv2011.0
+ Revision: 590961
- Bump to 1.5.21
- apply sidebar patch from http://spacehopper.org/mutt/sidebar-5302767aa6aa.gz
  (thanks lev for the tip)
- rediff most patches (see below for the touchy ones)
- comment out patch107 (merged upstream, peer review would be appreciated)
- nntp patch rediffed (peer review please ? :) )

* Mon Apr 05 2010 Eugeni Dodonov <eugeni@mandriva.com> 1:1.5.20-8mdv2010.1
+ Revision: 531864
- P7: properly handle subjectAltNames under openssl-1.0.0.

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.20-7mdv2010.1
+ Revision: 511592
- rebuilt against openssl-0.9.8m

* Mon Jan 25 2010 RÃ©my Clouard <shikamaru@mandriva.org> 1:1.5.20-6mdv2010.1
+ Revision: 496291
- add mutt-utf8 as a suggests

* Wed Jan 06 2010 RÃ©my Clouard <shikamaru@mandriva.org> 1:1.5.20-5mdv2010.1
+ Revision: 486870
- fix a bug where hilighted line in the index was wrongly redrawn

* Sun Jan 03 2010 RÃ©my Clouard <shikamaru@mandriva.org> 1:1.5.20-4mdv2010.1
+ Revision: 485893
- add patch from previous commit
- add indexcolor patch

* Fri Jan 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.20-3mdv2010.1
+ Revision: 484725
- rebuilt against bdb 4.8

* Thu Oct 08 2009 Eugeni Dodonov <eugeni@mandriva.com> 1:1.5.20-2mdv2010.0
+ Revision: 455940
- Updated to new sidebar patch.

* Wed Sep 23 2009 JÃ©rÃ´me Quelin <jquelin@mandriva.org> 1:1.5.20-1mdv2010.0
+ Revision: 447815
- oops, should reset rel
- update to 1.5.20
- updated manually gpg patch (don't we have an upstream url?
- updated vvv and rr.compressed patches with their upstream version
- removed sidebar patch which is not maintained upstream, doesn't apply
  cleanly, and is not really useful (i was the original requester for
  its inclusion)

* Wed Sep 23 2009 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.19-2mdv2010.0
+ Revision: 447772
- P106: security fix for CVE-2009-1390 (redhat)
- P107: security fix for nul cert spoof

* Tue Jun 16 2009 Lev Givon <lev@mandriva.org> 1:1.5.19-1mdv2010.0
+ Revision: 386370
- Update to 1.5.19.
  Update included external patches (nntp, compression, sidebar).

* Mon Dec 15 2008 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.18-2mdv2009.1
+ Revision: 314512
- rediffed fuzzy patches
- rebuilt against db4.7

* Sun Jul 06 2008 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 1:1.5.18-1mdv2009.0
+ Revision: 232031
- Updated to version 1.5.18
- Rediffed urlview patch.
- Added updated versions of included external patches (compressed folder
  support, NNTP support and Sidebar support).

* Thu Jan 24 2008 Ademar de Souza Reis Jr <ademar@mandriva.com.br> 1:1.5.17-5mdv2008.1
+ Revision: 157701
- add mailcap as suggestion (w/out it, .pdfs are attached as
  text/plain and get scrambled)

* Thu Jan 03 2008 JÃ©rÃ´me Quelin <jquelin@mandriva.org> 1:1.5.17-4mdv2008.1
+ Revision: 142102
- adding sidebar support (fixing bug 29371)

* Thu Dec 27 2007 Oden Eriksson <oeriksson@mandriva.com> 1:1.5.17-3mdv2008.1
+ Revision: 138191
- rebuilt against bdb 4.6.x libs

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Nov 12 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.17-2mdv2008.1
+ Revision: 108133
- rebuild to get correct permissions on manpages (lzma bug)

* Mon Nov 05 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.17-1mdv2008.1
+ Revision: 106022
- updated to version 1.5.17

  + Thierry Vignaud <tv@mandriva.org>
    - s/mandrake/mandriva/

* Fri Sep 21 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.16-4mdv2008.0
+ Revision: 92110
- mutt doesn't need an external MTA anymore: it has builtin smtp support now

* Mon Sep 17 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.16-3mdv2008.0
+ Revision: 89320
- drop CVE-2006-5298 patch, it was already fixed upstream in a different way (#29916)

* Wed Jun 27 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.16-2mdv2008.0
+ Revision: 45052
- rebuild with new rpm-mandriva-setup (-fstack-protector)

* Thu Jun 21 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.16-1mdv2008.0
+ Revision: 42310
- updated to version 1.5.16
- fixed doc dir according to new policy
- dropped CVE-2007-2683 security patch, already applied
- redid/updated urlview, nntp and compressed patches
- added security fix for CVE-2007-2683 (Closes: #31191)

* Wed May 16 2007 Gustavo De Nardin <gustavodn@mandriva.com> 1:1.5.15-4mdv2008.0
+ Revision: 27316
- renamed just introduced mutt-manual subpackage to mutt-doc (no Obsoletes)

* Wed May 16 2007 Gustavo De Nardin <gustavodn@mandriva.com> 1:1.5.15-3mdv2008.0
+ Revision: 27137
- introduce mutt-manual subpackage, with the full manual for Mutt

* Wed May 02 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.5.15-2mdv2008.0
+ Revision: 20595
- disabled parallel make, doesn't work
- forgot to enable smtp support
- updated to version 1.5.15 (smtp support \o/)
- updated patches for this version


* Fri Mar 02 2007 Andreas Hasenack <andreas@mandriva.com> 1.5.14-1mdv2007.0
+ Revision: 131589
- updated to version 1.5.14
- removed CVE-2006-5297 patch, already applied
- updated external patches

* Wed Nov 29 2006 Andreas Hasenack <andreas@mandriva.com> 1:1.5.13-1mdv2007.1
+ Revision: 88789
- updated to version 1.5.13
- updated many patches

* Mon Oct 30 2006 Andreas Hasenack <andreas@mandriva.com> 1:1.5.11-6mdv2007.1
+ Revision: 73825
- added patches for CVE-2006-5297 and CVE-2006-5298
  (#26787)
- rebuild with new ncurses (5.5-1.20051029.3mdv2007.0)
- reverted back to 1.5.11: 1.5.12 as it was committed doesn't build
  and we are in freeze anyway

  + JÃ©rÃ´me Soyer <saispo@mandriva.org>
    - Remove patch105
    - New release 1.5.12

* Sat Jul 01 2006 Andreas Hasenack <andreas@mandriva.com> 1:1.5.11-4mdv2007.0
+ Revision: 38203
- bunzipped the remaining patches
- added security patch for CVE-2006-3242 (#23424)
- import mutt-1.5.11-3mdv2007.0

* Wed May 31 2006 Pablo Saratxaga <pablo@mandriva.com> 1.5.11-3mdk
- use aspell instead of ispell
- set paths to gpg, so it works out of the box (if gpg installed)
- corrected bug when calling external programs to view attached files

* Sun Nov 13 2005 Oden Eriksson <oeriksson@mandriva.com> 1.5.11-2mdk
- rebuilt against openssl-0.9.8a

* Sat Oct 01 2005 Andreas Hasenack <andreas@mandriva.com> 1.5.10i-1mdk
- updated to version 1.5.11 (no "i" from now on)
- removed thread patch, already applied
- updated nntp patch
- updated compressed folders patch

* Wed Aug 31 2005 Frederic Lepied <flepied@mandriva.com> 1.5.9i-9mdk
- removed BuildRequires on ispell as it's not in main anymore

* Wed Jul 27 2005 Nicolas Lécureuil <neoclust@mandriva.org> 1.5.9i-8mdk
- Fix smtpdaemon on BuildRequire
- %% mkrel

* Tue Jul 12 2005 Andreas Hasenack <andreas@mandriva.com> 1.5.9i-7mdk
- changed Requires from smtpdaemon to sendmail-command

* Tue Apr 26 2005 Andreas Hasenack <andreas@mandrivalinux.com> 1.5.9i-6mdk
- updated to version 1.5.9i
- removed P5, it's already fixed in this version
- updated compressed folder patch for this version
- updated nntp patch for this version
- removed hcache patch, the imap part is already applied and is actually
  the more important one (maildir is already fast)
- redid edit-threads patch for this version
- updated save_history patch to version 1.5.6 (latest available at this time)
- using current autoconf/automake now as it is compatible with the new nntp
  patch version

* Wed Mar 30 2005 Andreas Hasenack <andreas@mandrakesoft.com> 1.5.6i-5mdk
- just a rebuild and a release increase, since the last package never went
  into cooker

* Sun Mar 13 2005 Andreas Hasenack <andreas@mandrakesoft.com> 1.5.6i-4mdk
- added conditional sasl2 build (enabled by default) (Closes: #14221)
- added configure options to honor kerberos build which was previously
  only relying on a buildrequires
- since mutt is built twice, use a shell function instead of calling
  configure/make "inline"
- added header cache patch with the Makefile.am hunk slightly modified
  because of the nntp patch
- added libdb4.2-devel buildrequires because of the header_cache patch.
  This patch can use either BDB or GDBM: I prefer BDB.
- added P5 to fix #13020

* Wed Jan 12 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.5.6i-3mdk
- fix buildrequires

* Wed Jun 02 2004 Marcel Pol <mpol@mandrake.org> 1.5.6i-2mdk
- buildrequires autoconf2.1 (slbd)

* Sat Apr 17 2004 Abel Cheung <deaddog@deaddog.org> 1.5.6i-1mdk
- New version
- Regen patches


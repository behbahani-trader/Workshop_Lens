@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXPROJ=lens-workshop

if "%1" == "" goto help

if "%1" == "help" (
	:help
	@echo.
	@echo Usage: make ^<target^> where target is one of
	@echo   html       to make standalone HTML files
	@echo   dirhtml    to make HTML files named index.html in directories
	@echo   singlehtml to make a single large HTML file
	@echo   pickle     to make pickle files
	@echo   json       to make JSON files
	@echo   htmlhelp   to make HTML files and a HTML help project
	@echo   qthelp     to make HTML files and a qthelp project
	@echo   applehelp  to make an Apple Help Book
	@echo   devhelp    to make HTML files and a Devhelp project
	@echo   epub       to make an epub
	@echo   epub3      to make an epub3
	@echo   latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter
	@echo   latexpdf   to make LaTeX files and run them through pdflatex
	@echo   latexpdfja to make LaTeX files and run them through platex/dvipdfmx
	@echo   text       to make text files
	@echo   man        to make manual pages
	@echo   texinfo    to make Texinfo files
	@echo   info       to make Texinfo files and run them through makeinfo
	@echo   gettext    to make PO message catalogs
	@echo   changes    to make an overview of all changed/added/deprecated items
	@echo   xml        to make Docutils-native XML files
	@echo   pseudoxml  to make pseudoxml-XML files for display purposes
	@echo   linkcheck  to check all external links for integrity
	@echo   doctest    to run all doctests embedded in the documentation (if enabled)
	@echo   coverage   to run coverage check of the documentation (if enabled)
	@echo   dummy      to check syntax errors of document sources
	@echo.
	goto end
)

if "%1" == "clean" (
	for /d %%i in (%BUILDDIR%\*) do rmdir /s /q %%i
	del /q /s %BUILDDIR%\*
	goto end
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd 
# viat

A tool for managing **vi**rtual file **at**tributes.

## Motivation

When managing lots of files, there comes a point when metadata needs to be attached to them somehow.

* Different file systems offer [extended file attributes](https://en.wikipedia.org/wiki/Extended_file_attributes). Unfortunately, poor software support reduces their utility. For example, `curl --xattr <url>` will record some attributes, but they will be lost on copy (with GNU `cp` at least) and will not be tracked by git.

* [git attributes](https://git-scm.com/docs/gitattributes) are obviously supported by git, but other tools have to consult git in order to use them. Furthermore, there is no convenient mechanism for setting git attributes.

* XMP ([extensible metadata platform](https://developer.adobe.com/xmp/docs/)) files are designed to be used by arbitrary tools and can be easily tracked using version control, but are cumbersome to manage.

Perhaps I am missing some other approaches, but at this point it should be clear that there is no convenient way to manage file metadata. A long time ago I wrote a small script that tracked "virtual" attributes across a directory by putting them into a single JSON file. I needing variations of the script every now and then, so I ended up creating this tool.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

* Allow disabling validation.
* Fix not being to select the JSON storage provider.
* Remove short option for tracked --no-data.
* Move error stringification into the error hierarchy.

## 0.9.6 - 2026-05-12

* Refactor vault location.
* Rename `MissingAttributeError` -> `ViatMissingAttributeError`.

## 0.9.5 - 2026-05-12

* Traverse parent directories when autoloading the vault (e.g. all CLI operations).
* Always display validation errors when checking tracked files.
* Remove obsolete module check for click.

## 0.9.4 - 2026-05-12

* Fix misconfigured dependency version specifiers.

## 0.9.3 - 2026-05-12

* Add a configuration documentation
* Make click a mandatory dependency to avoid installation complications.

## 0.9.2 - 2026-05-12

* Configure publishing on PyPI.

## 0.9.1 - 2026-05-12

* Fix man file build complications.

## 0.9.0 - 2026-05-12

* Initial release.

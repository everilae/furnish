ChangeLog
=========

0.2.1
-----

- Added `Json` and `File` annotations for sending JSON encoded data and
  files respectively.
- `Response.body()` will raise an error, if response status is 4xx or 5xx.
- Use `typing` instead of `backports.typing`.

0.2.0
-----

- Added `furnish.create()` client factory.
- Added `@furnish.headers` decorator for setting static headers.
- Removed `@furnish.furnish` class decorator.

0.1.2
-----

- Added simple object deserialization.

0.1.1
-----

- Fixed formatting for PyPi.

0.1.0
-----

- Initial release.

# MyVer

[![Build Status][workflow-badge]][workflow-link]
[![Coverage][coverage-badge]][coverage-link]
[![Version][version-badge]][version-link]
[![MIT License][license-badge]](LICENSE.md)

---

MyVer is a tool to help you manage and alter your project's version
number. You can define your own configuration for your version, MyVer
gives you complete freedom to enforce your own version spec, make it as
simple or as complex as you need it to be.

# Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
  - [YAML Syntax](#yaml-syntax)
    - [`files`](#files)
    - [`files[*].path`](#filespath)
    - [`files[*].patterns`](#filespatterns)
    - [`parts`](#parts)
    - [`parts.<part>`](#partspart)
    - [`parts.<part>.value`](#partspartvalue)
    - [`parts.<part>.requires`](#partspartrequires)
    - [`parts.<part>.prefix`](#partspartprefix)
    - [`parts.<part>.identifier`](#partspartidentifier)
    - [`parts.<part>.identifier.strings`](#partspartidentifierstrings)
    - [`parts.<part>.identifier.start`](#partspartidentifierstart)
    - [`parts.<part>.number`](#partspartnumber)
    - [`parts.<part>.number.label`](#partspartnumberlabel)
    - [`parts.<part>.number.label-suffix`](#partspartnumberlabel-suffix)
    - [`parts.<part>.number.start`](#partspartnumberstart)
    - [`parts.<part>.number.show-start`](#partspartnumbershow-start)
- [Examples](#examples)
  - [SemVer](#semver)
    - [Standard bumping scenarios](#standard-bumping-scenarios)
    - [Bumping with non-required child](#bumping-with-non-required-child)
    - [Part with a required child](#part-with-a-required-child)
    - [Value overriding](#value-overriding)
    - [Resetting optional part](#resetting-optional-part)
    - [Implicit children](#implicit-children)

# Installation

To install MyVer you can use [pip](https://pypi.org/project/pip/), which
will download and install the 
[MyVer package from PyPi](https://pypi.org/project/myver/)

```bash
pip install myver
```

# Usage

```
usage: myver [-h] [-c] [-b ARG [...]] [-r PART [...]] [--config PATH]

  -h, --help               Show this help message and exit
  -c, --current            Get the current version
  -b, --bump ARG [...]     Bump version parts
  -r, --reset PART [...]   Reset version parts
  --config PATH            Config file path
```

# Configuration

This section will describe the configurations YAML syntax. This is for a
detailed explanation of each attribute in the configuration. While
examples may be present in this section, it is also beneficial to refer
to the [Examples](#examples) section to see full practical
implementations of the configuration YAML.

## YAML Syntax

### `files`

*Optional*. A list of files to update when the version is changed. It
will only change references to the current version value by default.

An unwanted file change is possible if you are referencing the version
of another project in a file that happens to have the same version
string as your project, then both instances of that version string will
be updated. So lets say your project's version is `3.6.8`
and you are updating a file that is referencing `Python 3.6.8`, then by
default the python version reference will be updated. Although these
unwanted file updates can be avoided with further configuration.

```yaml
files:
  - path: 'setup.py'
    patterns:
      - "version='{{ version }}'"
  - path: '/project/__version__.py'
```

### `files[*].path`

The path to a file that you want to update with each version change.
This path can use
[globbing](https://en.wikipedia.org/wiki/Glob_(programming)) so that you
can define a range of files to update.

```yaml
files:
  - path: '/path/to/file.md'
  - path: '/can/also/glob/*.txt'
```

### `files[*].patterns`

List of regex patterns to use for updating a file. Any instance of a
version string will not be updated if it does not match a pattern. The
pattern regex strings must contain `{{ version }}` to parse the current
version into the pattern, this will be parsed first before the regex is
utilised in searching for file updates. We need to include
`{{ version }}` because this signifies the part of the string to change
in a pattern match.

If `files[*].patterns` is not configured, it is assumed that the default
pattern match is just `{{ version }}`, meaning that any string in the
file that is equal to the current version will be updated.

```yaml
files:
  - path: 'setup.py'
    patterns:
      - "version='{{ version }}'"
```

### `parts`

*Required*. Collection of parts configured for your project's version.
You must define at least 1 [`parts.<part>`](#partspart) in this
collection.

### `parts.<part>`

The configuration of an individual part in a version. You define the key
of the part through the name of the YAML attribute, in the example
below the key of our only part is `major`, you can name these keys
whatever you like, although you cannot have 2 parts with the same key
name.

There are 2 types of parts -- identifier parts and number parts. An
identifier part is a string part that can have a value based on a range
of strings, see [`parts.<part>.identifier`](#partspartidentifier).
Whereas a number part is simply a positive integer that can be
incremented. The number part is the default type if a type is not
explicitly configured.

```yaml
parts:
  major:
    value: 3
 ```

### `parts.<part>.value`

Each part configuration needs to define a value attribute in its spec.
If your part has no value then use `value: null`. Depending on the part
type, the value of the part can be a string or a number. All parts can
also be `null`.

```yaml
parts:
  major:
    value: 3
  minor:
    value: null
  pre:
    value: 'beta'
    identifier:
      strings: [ 'beta' ]
 ```

### `parts.<part>.requires`

Defines a part that is required to exist by another part. It means that
if a part has a non-null value, and it requires another part, the part
that it requires cannot be null. In the example below we see that
`major` requires `minor`, this means that `minor` can only ever be null
if `major` is null. So if `major` has a non-null value, then `minor`
must also have a non-null value.

```yaml
parts:
  major:
    value: 3
    requires: 'minor'
  minor:
    value: 9
 ```

### `parts.<part>.prefix`

A string to display before the part. In the example below we have part
`major` and `minor`, if we parse this version we will get `3.9`, where
the `.9` is the `minor` part where the `.` is the prefix of the part's
value.

```yaml
parts:
  major:
    value: 3
  minor:
    value: 9
    prefix: '.'
 ```

### `parts.<part>.identifier`

When this is configured on a part, it signifies that the part value is
a string. *You cannot configure `parts.<part>.identifier` and
[`parts.<part>.number`](#partspartnumber) at the same time, they are
mutually exclusive.*

You would use this when you have multiple possible strings for a part
that have a chronological order between each string. A common example
are the pre-release identifiers of `alpha`, `beta`, and `rc`.

### `parts.<part>.identifier.strings`

A list of strings to be used in the part's value, if you have configured
[`parts.<part>.identifier`](#partspartidentifier) for a part, then this
list of strings needs to be configured. The order of the strings matter
as the bumping of an identifier part will move through the list in the
order it is defined.

```yaml
parts:
  pre:
    identifier:
      strings:
        - 'alpha'
        - 'beta'
        - 'rc'
```

### `parts.<part>.identifier.start`

The starting value for the part. The start value is the value that the
part will use when it is bumped from a `null` value, or when it is
reset. By default, if this is not configured explicitly, the start value
is assumed to be the first value in the
[`parts.<part>.identifier.strings`](#partspartidentifierstrings) list.

```yaml
parts:
  pre:
    value: 'beta'
    identifier:
      strings:
        - 'alpha'
        - 'beta'
        - 'rc'
      start: 'beta'
```

### `parts.<part>.number`

This will configure a part to be a positive integer. *You cannot
configure [`parts.<part>.identifier`](#partspartidentifier) and
`parts.<part>.number` at the same time, they are mutually exclusive.*

### `parts.<part>.number.label`

Sometimes you will want a label for a number part. In the example below
we have a `build` part, instead of just using a number to represent this
part, you may instead want to parse it to something like `build4`, and
this is what the example below achieves.

```yaml
parts:
  build:
    value: 4
    number:
      label: 'build'
```

### `parts.<part>.number.label-suffix`

A label may have a suffix (characters after the label) in order to
separate the label with the number. In the example below we see the `.`
suffix on a `build` label, which would give something like `build.4`
when it is parsed.

```yaml
parts:
  build:
    value: 4
    number:
      label: 'build'
      label-suffix: '.'
```

### `parts.<part>.number.start`

This defines the starting value for a number part, this the value that
the part will use when it is bumped out of a `null` value, or if it is
reset. By default, it is assumed that the start value of a number part
is `0` if it is not configured explicitly.

```yaml
parts:
  build:
    value: 4
    number:
      start: 1
```

### `parts.<part>.number.show-start`

Sometimes you may not want to show the first value of a number part. In
the example below we have a `dev` part, commonly you may see a version
like `3.4.5+dev` which would define the first dev instance of a version,
then the second dev instance would look like this `3.4.5+dev.2`. By
default, this value will be assumed to be `true` if it is not
configured explicitly.

```yaml
parts:
  dev:
    value: 1
    number:
      label: 'dev'
      label-suffix: '.'
      start: 1
      show-start: false
```

# Examples

## SemVer

This file handles how the version is formed. It will store the current
values of each part, and it will also define the configuration of each
part.

```yaml
parts:
  major:
    value: 3
    requires: minor

  minor:
    value: 9
    prefix: '.'
    requires: patch

  patch:
    value: 2
    prefix: '.'

  pre:
    value: null
    prefix: '-'
    requires: prenum
    identifier:
      strings: [ 'alpha', 'beta', 'rc' ]

  prenum:
    prefix: '.'
    value: null
    number:
      start: 1

  build:
    value: null
    prefix: '+'
    number:
      label: 'build'
      label-suffix: '.'
      start: 1

  dev:
    value: null
    prefix: '+'
    number:
      label: 'build'
      label-suffix: '.'
      start: 1
      show-start: false
```

### Preamble

In each of these scenarios we will show a snippet which is demonstrating
how you may interact with MyVer in a terminal environment. There may
then be a description of what is happening in the snippet demonstration
below each snippet.

### Standard bumping scenarios

```shell
myver --current
> 3.8.2
myver --bump patch
> 3.8.3
myver --bump minor
> 3.9.0
```

### Bumping with non-required child

```shell
myver --current
> 3.8.2
myver --bump patch dev
> 3.8.3+dev
```

In this example we show how the part ordering matters in the config. We
can see that the `dev` part is configured after the `patch` part, and
the `patch` part does not require any other part. This means that `dev`
is a valid child for the `patch` part.

```shell
myver --current
> 3.8.3+dev
myver --bump patch
> 3.8.4
```

It is also important to keep in mind that non-required child parts will
be removed when its parent is bumped if you do not ask to keep the child
part. In the above example we bump `patch` and the `dev` part gets
removed, if we wanted to have the `dev` part in the bumped version then
we would have to be more explicit and use `myver --bump patch dev`.

### Part with a required child

```shell
myver --current
> 3.8.2
myver --bump patch pre
> 3.8.3-alpha.1
```

We see that specifying `pre` to be brought along with the bump of
`patch`, also brings along `prenum`. This is because `prenum` is
configured to be required by `pre`.

Also note that having a null part and attempting to bump it will set it
at its starting value, and it will bring along its required child if it
has one. A starting value by default is the first value in the list of
its `strings` in the `identifier` configuration. In this case we see
that `pre` starts with the value of `alpha`. If it is a number part then
the start value is `0` by default.

### Value overriding

```shell
myver --current
> 3.8.2
myver --bump minor pre=beta
> 3.9.0-beta.1
myver --bump patch=5
> 3.9.5
```

Sometimes you may not want to use the start value of a string part. Here
we see that `pre` is an identifier part (which is implied through having
its `identifier` configuration). By providing the `'='` character and a
valid identifier directly after `pre`, it will use that identifier value
for the `pre` part, in this case it is `beta`, which is skipping
the `alhpa` value. It is important that you specify a part value that is
valid (i.e. it is in the `strings` list in the `identifier`
configuration of the part)

We can also do the same for number parts, above we see that we used
value overriding to set `patch` to `5`. For a number part, you cannot
set the value to a negative number, and it cannot be a string either, it
must be an integer.

### Resetting optional part

```shell
myver --current
> 3.9.0-beta.1+build.34
myver --reset pre
> 3.9.0
```

You may want to remove a part, this can easily be done with the
`--reset` option. In the above scenario we see that resetting an
optional part will also reset its descendants. Although we can keep a
descendant if we use `--bump`.

```shell
myver --current
> 3.9.0-beta.1+build.34
myver --reset pre --bump build
> 3.9.0+build.1
```

### Implicit children

This may not even need to be explained as it is supposed to be
intuitive, although I am including this section just to explain the
implicit children in a technical way so that people can debug any of
their use cases which may be acting weird due to this feature. So you do
not have to understand this section to make use of implicit children, it
should hopefully come to you naturally.

```shell
myver --current
> 3.8.2+build.1
# Reads as: bump patch, with pre, with dev
myver --bump dev
> 3.8.2+build.1-dev
```

This is the clearest example of implicit children, in the config we do
not explicitly define the `dev` part to be required by the `buildnum`
part, yet it becomes a child of `buildnum` when we add `dev` in a bump.
This is due to the order of the parts in the config, and also due to
`dev` not being a required child of any other parts, so the only logical
place to put the `dev` part is after the last part that has a value,
which in this case is `buildnum`.

```shell
myver --current
> 3.8.2+build.1-dev
# Reads as: bump patch, with pre, with dev
myver --bump buildnum
> 3.8.2+build.2
```

Also keep in mind that implicit children will be removed if their parent
is bumped. In the above example if you wanted to keep `dev` you need to
be explicit and use `myver --bump buildnum dev`

```shell
myver --current
> 3.8.2
# Reads as: bump patch, with pre, with dev
myver --bump patch pre dev
> 3.8.3-alpha.1+dev
```

When bumping `patch` with `pre`, the `pre` will bring along its `prenum`
child since it is a required part. Although how did we bring along `dev`
with `prenum` if we do not specify `prenum` in the arguments of the
command? In this scenario we can say that `dev` is implicitly a child of
the `prenum` part, and this happens due to `prenum` being a required
child of `pre`, and `prenum` is also defined before the `dev` part is
defined in the config, so it takes precedence.

So why are we allowed to ignore the `build` part? It's because
the `build` part is not required by any other part that is current set.

```shell
myver --current
> 3.8.3-alpha.1+dev
# Reads as: bump build
myver --bump build
> 3.8.3-alpha.1+build.1
```

Why did the `dev` part get removed in this case? This is because of the
ordering of the parts in the config. When an implicit parent-child
relationship is broken, the original child part is removed. In this
scenario the `prenum` and `dev` implicit relationship is broken because
adding the `build` and `buildnum` part introduces a new implicit child
for `prenum`. The `build` part is defined in the config before `dev` is
defined, so it takes precedence, which is why we do not get a new
version of something like `3.8.3-alpha.1+dev-build.1`

This scenario is a simple config, so it may be reasonable to think that
we should just keep the `dev` and make it a child of the `buildnum`
part, but what happens in more complex scenarios with many possible
implicit children? Also, it is not a good thing to freely shift parts
around as a side effect of bumping other parts, the command should
explicitly ask for a version outcome. In other words, having `dev` as a
child of one part, has no chronological relation with a different part
having `dev` as its child, they are both dev instances of completely
different versions. Since `myver --bump build` does not explicitly ask
for `dev` to be in the bumped version, then we should not provide a
version that is not explicitly asked for.


[version-badge]: https://img.shields.io/pypi/v/myver.svg?label=version

[version-link]: https://pypi.python.org/pypi/myver/

[coverage-badge]: https://coveralls.io/repos/github/mark-bromell/myver/badge.svg?branch=main

[coverage-link]: https://coveralls.io/github/mark-bromell/myver?branch=main

[workflow-badge]: https://github.com/mark-bromell/myver/workflows/Tests/badge.svg

[workflow-link]: https://github.com/mark-bromell/myver/actions?query=workflow%3ATests

[license-badge]: https://img.shields.io/badge/license-MIT-007EC7.svg

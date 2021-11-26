# MyVer

[![Build Status][workflow-badge]][workflow-link]
[![Coverage][coverage-badge]][coverage-link]
[![Version][version-badge]][version-link]
[![MIT License][license-badge]](LICENSE.md)

---

# Configuration

Here is the fields that are available in the configuration's yaml. The
comments in this snippet may not cover the full scope of each field and
what it entails, so we recommend reading the [Examples](#examples)
section to further understand how myver works, and also how to know how
the configuration affects the version

```yaml
# optional
# Files to update the version in.
files:
  - path: '/path/to/file.md'
  - path: '/can/also/glob/*.txt'
    ignores:  # Update all version occurrences except these.
      - '.*=={{ version }}'
  - path: 'setup.py'
    patterns:  # Only update based on these patterns, ignore the rest.
      - "version='{{ version }}'"

# required
# Put each of your part elements inside here.
parts:
  # required (at least 1)
  # This is one of our parts with its key named `main`.
  main:
    # string | int | null -- required
    # If you do not define a part value, it will use the start value if
    # it is invoked in a bump. If a part value is null, then it will not
    # be shown in the version.
    value: null

    # string | null -- optional
    # Defines any other part that this part requires. This means that
    # `main` cannot exist without having its required part as a direct 
    # child of this part. Value must be a valid part name.
    requires: null

    # string | null -- optional
    # Parts may have a character prefix in order to visually separate
    # them from previous parts, or to denote more meaning to the part.
    prefix: null

    # You can either have `identifier` or `number`, you cannot have
    # both. If neither is configured, then the part will be configured
    # as a number part, with a default start value of `0`.

    # optional
    # This configures a part to be an identifier string. You would use
    # this when you have multiple possible strings for a part that have
    # a chronological order between each string. A common example are
    # the pre-release identifiers of `alpha`, `beta`, and `rc`.
    identifier:
      # list -- required
      # These are the strings which should be listed in their
      # chronological order.
      strings: [ 'string1', 'string2' ]

      # string -- optional
      # You can define a custom start value, by default the start value
      # will be the first value in the `strings` list. If you do define
      # a custom start value, it needs to be a value that is also in the
      # string list.
      start: 'string1'

    # optional
    # This configures a part to be a number. This means that it is
    # easily incremented, and it cannot contain alphabetic characters.
    number:
      # string | null -- optional
      # Sometimes you will want a label for a number part. An example
      # of this would be a `build` part, instead of just using a number
      # to represent this part, you may instead see something like
      # `build.4` as a part.
      label: null

      # string | null -- optional
      # A label may have a suffix (characters after the label) in order
      # to separate the label with the number. An example of this would
      # be the `.` suffix on a `build` label, which would give something
      # like `build.4` as a part.
      label-suffix: null

      # int -- optional
      # When the part is reset or invoked, this is the value that the
      # part will start at. By default, number parts start at 0.
      start: 0

      # boolean -- optional
      # Sometimes you may not want to show the first value of a number
      # part. An example of this would be a `dev` part, commonly you
      # may see a version like `3.4.5+dev` which would define the first
      # dev instance of a version, then the second dev instance would
      # look like this `3.4.5+dev.2`.
      show-start: true

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
how you may interact with myver in a terminal environment. There may
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

# Configuration

Here is the fields that are available in the configuration's yaml. The
comments in this snippet may not cover the full scope of each field and
what it entails, so we recommend reading the [Examples](#examples)
section to further understand how myver works, and also how to know how
the configuration affects the version

```yaml
# Put each group of parts in here.
groups:
  # This is a group named `core`.
  core:
    # Defines the prefix for the group as a whole, this prefix will override
    # the prefix of the first occurring part of the group (that is if the first
    # part of the group even has a prefix).
    prefix: null

    # Put each of your part elements inside here.
    parts:
      # This is one of our parts named `mypart`.
      mypart:
        # Defines any other part that this part requires. This means that
        # `mypart` cannot exist without having its required part as a direct
        # child of this part.
        requires: null

        # Parts may have a character prefix in order to visually separate
        # them from previous parts, or to denote more meaning to the part.
        prefix: null

        # List of strings that can be potential values in a part. Can only
        # be used if the part is not numeric (numeric: false).
        identifiers: null

        # Numerics can be incremented with no limit. If numeric is false
        # then incrementing cannot occur. If you want a part to be a custom
        # string without any identifier constraints, set `numeric` to false
        # and leave `identifiers` as null. This would mean you need to define
        # the string value for the part each time you want to bump with it.
        numeric: true

        # Since parts are numeric by default, then this is the starting
        # point by default.
        start: 0

        # If you do not define a part value, it will use the start value if
        # it is invoked in a bump. If a part value is null, then it will not
        # be shown in the version.
        value: null
```

# Examples

## SemVer

This file handles how the version is formed. It will store the current
values of each part, and it will also define the configuration of each
part.

```yaml
groups:
  core:
    parts:
      major:
        requires: minor
        value: 3

      minor:
        requires: patch
        prefix: '.'
        value: 8

      patch:
        prefix: '.'
        value: 2

  pre:
    prefix: '-'
    parts:
      pre:
        requires: prenum
        identifiers: [ alpha, beta, rc ]
        value: null

      prenum:
        prefix: '.'
        start: 1
        value: null

  meta:
    prefix: '+'
    parts:
      build:
        requires: buildnum
        identifiers: [ build ]
        value: null

      buildnum:
        prefix: '.'
        start: 1
        value: null

      dev:
        identifiers: [ dev ]
        prefix: '-'
        value: null

      devnum:
        prefix: '.'
        start: 2
        value: null
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

As you can see, we do not need to specify the group that a part is in.
Grouping in this example is strategic, which we discuss in the
[Prefix priority](#prefix-priority) scenario.

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

Also note that having and null part and attempting to bump it will start
it at its starting value, and it will bring along its required child if
it has one. A starting value by default is the first value in the list
of its `identifiers`. In this case we see that `pre` starts with the
value of `alpha`. If there is no list of `identifiers` then the starting
value is `0` since a part defaults to be numeric.

### Prefix priority

```shell
myver --current
> 3.8.2
myver --bump patch dev
> 3.8.3+dev
myver --bump patch build dev
> 3.8.4+build.1-dev
```

The `dev` part is configured to have a prefix of `'-'`, although in the
first bump of this scenario, it has a `'+'`, what's going on here? This
is because the group prefix takes priority of the part prefix. The `dev`
part is in the `meta` group, and the `meta` group has a prefix of `'+'`,
so no matter the prefix of a part, if it is the first part of a group,
it will use the prefix of the group instead of the part's prefix.

### Manually set the value of a string part

```shell
myver --current
> 3.8.2
myver --bump minor pre=beta
> 3.9.0-beta.1
myver --bump patch=5
> 3.9.5
```

```shell
myver --current
> 3.8.2
myver --bump minor pre=beta dev
> 3.9.0-beta.1+dev
```

Sometimes you may not want to use the start value of a string part. Here
we see that `pre` is a string part (which is implied through
its `identifiers` list of strings in the config). By providing the `'='`
character and a valid identifier directly after `pre`, it will use that
identifier value for the `pre` part, in this case it is `beta`, which is
skipping the `alhpa` value. It is important that you specify a part
value that is valid (i.e. it is in the `identifiers` list in the config
of the part)

### Deleting optional part

```shell
myver --current
> 3.9.0-beta.1+build.34
myver --delete pre
> 3.9.0
```

You may want to remove a part, this can easily be done with the
`--delete` option. In the above scenario we see that deleting an
optional part will also delete its descendants. Although we can keep a
descendant if we use `--bump`.

```shell
myver --current
> 3.9.0-beta.1+build.34
myver --delete pre --bump build
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

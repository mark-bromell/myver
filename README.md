# Examples

## SemVer

### `.simbump.yml` file

This file handles how the version is formed. It will store the current
values of each part, and it will also define the configuration of each
part.

```yaml
groups:
  core:
    children:
      - pre
      - meta
    parts:
      major:
        value: 3
        children:
          - minor
      minor:
        value: 8
        prefix: '.'
        children:
          - patch
      patch:
        value: 2
        prefix: '.'
  pre:
    prefix: '-'
    children:
      - meta
    parts:
      pre:
        value: null
        required: false
        identifiers:
          - alpha
          - beta
          - rc
        children:
          - prenum
      prenum:
        value: null
        start: 1
        prefix: '.'
  meta:
    prefix: '+'
    parts:
      build:
        value: null
        required: false
        identifiers:
          - build
        children:
          - buildnum
      buildnum:
        value: null
        start: 1
        prefix: '.'
      dev:
        value: null
        identifiers:
          - dev
        prefix: '-'
        children:
          - devnum
      devnum:
        value: null
        required: false
        start: 1
        prefix: '.'
```


### Standard bumping scenarios

```shell
simbump --current
> 3.8.2
simbump patch
> 3.8.3
simbump minor
> 3.9.0
```

As you can see, we do not need to specify the group that a part is in.
Grouping in this example is strategic, which we discuss in the
[Prefix priority](#semver-prefix-priority) scenario.


### Bumping with non-required child

```shell
simbump --current
> 3.8.2
# Reads as: bump patch, with dev
simbump patch dev
> 3.8.3+dev
```

In this example we show how the ordering in config of a
non-required part can be dynamic if it is the child of multiple parts.
The `dev` part can be a child of the `core` group or the `pre` group,
this is because both `core` and `pre` have the `meta` group as a child,
and `dev` is inside the meta group.


### <a name="semver-prefix-priority"></a>Prefix priority

```shell
simbump --current
> 3.8.2
simbump dev
> 3.8.2+dev
simbump patch build dev
> 3.8.3+build.1-dev
```

The `dev` part is configured to have a prefix of `'-'`, although in the
first bump of this scenario, it has a `'+'`, what's going on here? This
is because the group prefix takes priority of the part prefix. The `dev`
part is in the `meta` group, and the `meta` group has a prefix of `'+'`,
so no matter the prefix of a part, if it is the first part of a group,
it will use the prefix of the group instead of the part's prefix.


### Non-required part with a required child

```shell
simbump --current
> 3.8.2
# Reads as: bump patch, with pre
simbump patch pre
> 3.8.3-alpha.1
```

We see that specifying `pre` to be brought along with the bump of
`patch`, also brings along `prenum`. By default, every part is required,
but we configured `pre` to not be required, so when it is brought along
manually with a bump, any required parts in its descendants must be
brought along too.


### Manually set the value of a string part

```shell
simbump --current
> 3.8.2
# Reads as: bump minor, with pre as 'beta'
simbump minor pre --as beta
> 3.9.0-beta.1
```

```shell
# You can still do descendant chaining
simbump --current
> 3.8.1
# Reads as: bump minor, with pre as 'beta', with dev
simbump minor pre --as beta dev
> 3.9.0-beta.1+dev
```

Sometimes you may not want to use the start value of a string part. Here
we see that `pre` is a string part (which is implied through its 
`identifiers` list of strings in the config). By providing the `--as`
option directly after `pre`, it will use that `--as` value for the `pre`
part, in this case it is `beta`, which is skipping the
`alhpa` value. It is important that you specify a part value that is
valid (i.e. it is in the `identifiers` list in the config of the part)


### Deleting optional part

```shell
simbump --current
> 3.9.0-beta.1+build.34
simbump --delete pre
> 3.9.0
```

You may want to remove a part, this can easily be done with the 
`--delete` option. In the above scenario we see that deleting an
optional part will also delete its descendants. Although we can keep
a descendant if we use `--keep`.

```shell
simbump --current
> 3.9.0-beta.1+build.34
simbump --delete pre --keep build
> 3.9.0+build.1
```


## Introducing optional part

```shell
simbump --current
> 3.8.2
simbump pre
> 3.8.2-alpha.1
```

Having and empty optional part, and attempting to bump it will start it
at its starting value, and it will bring along any of its required
children. A starting value for a string part is the first value in the
list of its `identifiers`.


### Implicit children

```shell
simbump --current
> 3.8.2
# Reads as: bump patch, with pre, with dev
simbump patch pre dev
> 3.8.3-alpha.1+dev
```

Now it is getting a bit tricky, but it brings to light the way part
relationships work. When bumping `patch` with `pre`, the `pre` will
bring along its `prenum` child since it is a required part. Although how
did we bring along `dev` with `prenum` if we do not specify `prenum` in
the arguments of the command? In this scenario we can say that `dev` is
implicitly a child of the `prenum` part.

Since the `pre` group has the `meta` group as a child, and `dev` is in
the `meta` group, so `dev` is a valid descendant of the `pre` group. But
the `build` part is defined before the `dev` part, so why are we allowed
to ignore the `build` part? It's because the `build` part is optional,
and the `dev` part is not explicitly a child of any other part in the
`meta` group.

```shell
simbump --current
> 3.8.3-alpha.1+dev
# Reads as: bump prenum, with build
simbump prenum build
> 3.8.3-alpha.2+build.1
```

Why did the `dev` part get removed in this case? This is because of the 
ordering of the parts in the config. When a  parent-child relationship
is broken, the original child part is removed. In this scenario the
`prenum` and `dev` implicit relationship is broken because introducing
the `build` and `buildnum` part introduces a new implicit child for
`prenum`. 

This scenario is a simple config, so it may be reasonable to think that
we should just keep the `dev` and make it a child of the `buildnum`
part, but what happens in more complex scenarios with many possible
optional part relationships? Also, it is not a good thing to freely
shift parts around as a side effect of bumping other parts, the command
should explicitly ask for a version outcome. In other words, having
`dev` as a child of one part, has no chronological relation with a
different part having `dev` as its child, they are both dev instances of
completely different versions. Since `simbump prenum build` does not
explicitly ask for `dev` to be in the bumped version, then we should not
provide a version that is not explicitly asked for.

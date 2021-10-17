## Examples

### Example of `.simbump.yml` file

This file handles how the version is formed. It will store the current
values of each part, and it will also define the configuration of each
part.

```yaml
parts:
  major:
    value: 3
    children:
      - minor
  minor:
    value: 8
    prefix: '.'
    children:
      - micro
  micro:
    value: 1
    children:
      - pre
      - build
      - dev
  pre:
    value: ~
    prefix: '-'
    identifiers:
      - alpha
      - beta
      - rc
    children:
      - prenum
  prenum:
    value: ~
    prefix: '.'
    start: 1
    children:
      - build
      - dev
  build:
    value: ~
    prefix: '+'
    identifiers:
      - build
    children:
      - buildnum
  buildnum:
    value: ~
    prefix: '.'
    start: 1
  dev:
    value: ~
    prefix: '+'
    identifiers:
      - dev

```


#### Example of `.simbump.cfg` file

This file handles how the version as a whole (and its parts) are 
configured to work. Based on the parts discovered in `VERSION.cfg`,
simbump can then specify the configs of each part.

```ini
# .simbump.cfg
[simbump:micro]
children =
    pre
    build
    dev

[simbump:pre]
children = prenum
required = False
prefix = -
values = 
    alpha
    beta
    rc

[simbump:prenum]
children = 
    build
    dev
start = 1

[simbump:build]
required = False
prefix = +
values = build

[simbump:buildnum]
start = 1

[simbump:dev]
required = False
prefix = +
values = dev
```


### Standard bumping scenarios

```shell
simbump --current
> 3.8.1
simbump micro
> 3.8.2
simbump minor
> 3.9.0
```


### Bumping with non-required child

```shell
simbump --current
> 3.8.1
# Reads as: bump micro, with dev
simbump micro dev
> 3.8.2+dev
```

In this example we show how the ordering in `VERSION.cfg` of a
non-required part can be dynamic if it is the child of multiple parts.
The `dev` part can be a child of `micro` or `prenum`, although in
`VERSION.cfg` we see that `dev` has 4 parts in between itself and
`micro`! This does not matter, we can still just specify to bump `micro`
and bring in its non-required child of `dev`.


### Non-required part with a required child

```shell
simbump --current
> 3.8.1
# Reads as: bump micro, with pre
simbump micro pre
> 3.8.2-alpha.1
```

We see that specifying `pre` to be brought along with the bump of
`micro`, also brings along `prenum`. By default, every part is required,
but we configured `pre` to not be required, so when it is brought along
manually with a bump, any required parts in its descendants must be
brought along too.


### Non-required children and descendant chaining

```shell
simbump --current
> 3.8.1
# Reads as: bump micro, with pre, with dev
simbump micro pre dev
> 3.8.2-alpha.1+dev
```

Now it is getting a bit tricky, but it brings to light
the way part relationships work. When bumping `micro` with `pre`, the
`pre` will bring along its `prenum` child since it is a
required part. Although how did we bring along `dev` with
`prenum` if we do not specify `prenum` in the arguments of the command?
It is because `dev` may not be a child of `pre`, but it is still a
valid descendant, and `dev` will chain to the final descendant of the
`pre` part **only** if it can be a child of that final descendant. The
final descendant of `pre` in this scenario was `prenum` - and `dev`
can be a child of `prenum`.


### Manually set the value of a string part

```shell
simbump --current
> 3.8.1
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
`values` list of strings in the config). By providing the `--as`
option directly after `pre`, it will use that `--as` value for the `pre`
part, in this case it is `beta`, which is skipping the
`alhpa` value. It is important that you specify a part value that is
valid (i.e. it is in the `values` list in the config of the part)


## Option `--delete`

```shell
simbump --current
> 3.9.0-beta.1+dev
simbump --delete pre
> 3.9.0
```

```shell
simbump --current
> 3.9.0-beta.1+build.34
simbump --delete pre --keep build
> 3.9.0+build.1
```


## Option `--add`

```shell
simbump --current
> 3.8.1
simbump --add pre
> 3.8.1-alpha.1
```

```shell
simbump --current
> 3.9.0-beta.1+build.34
simbump --delete pre --keep build
> 3.9.0+build.1
```

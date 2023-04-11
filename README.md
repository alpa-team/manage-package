## Manage requests coming to your Alpa repo

This action manages issue requests coming from `alpa-cli` like request for deleting or
creating package.

### Who is this action for

For anybody who want their own instance of [Alpa](https://github.com/alpa-team) repository.

### Workflow yaml example

```yaml
name: Autoupdate Alpa repository

on:
  issues:
    types: [opened]

jobs:
  manage:
    runs-on: ubuntu-latest

  steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: React to new issue
      uses: alpa-team/manage-package@<tag_name>
      with:
        copr-login: ${{ secrets.COPR_LOGIN }}
        copr-token: ${{ secrets.COPR_TOKEN }}
        gh-api-token: ${{ secrets.GH_API_TOKEN }}
        debug: true
```

### Options

#### copr-login

_required_

Warning! Use GitHub secret instead of copy-pasting it to visible code directly!

login part from https://copr.fedorainfracloud.org/api/

#### copr-token

_required_

Warning! Use GitHub secret instead of copy-pasting it to visible code directly!

token part from https://copr.fedorainfracloud.org/api/

#### gh-api-token

_required_

Warning! Use GitHub secret instead of copy-pasting it to visible code directly!

GH API token with read/write permissions

#### debug

_not required_

Set to `true` if you want to see debug logs. Otherwise set to `false`.

# SageMaker Extension 0.6.0, released 2023-12-21

Code name: Added language container deployment

## Summary

This release includes api and cli for language container deployment. This is now consistent with
similar features of the Transformers extension.

**Note**: Most of the language container deployment code will be moved eventually to the
script-language-container-tool repository.

### Features

n/a
  
### Bug Fixes

n/a
  
### Documentation

n/a

### Refactoring

- #97: Improving the container deployment using the container deployer from [transformers-extension](https://github.com/exasol/transformers-extension/)  
- #99: Making the scripts deployer accepting a pyexasol connection
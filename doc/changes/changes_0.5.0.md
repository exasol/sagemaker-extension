# SageMaker Extension 0.5.0, released 2023-08-21

Code name: Enabled encryption for pyexasol

## Summary

This release enabled encryption for the pyexasol connections used in this project 
to fix connection issues with newer Exasol DB versions.

**Note**: Currently, we deactivated the SSL verification, we are going to fix this in this [issue](https://github.com/exasol/sagemaker-extension/issues/86). 

### Features

n/a
  
### Bug Fixes

  - #83: Add encryption and ignore SSL verification to pyexasol.connect calls
  
### Documentation

n/a
  
### Refactoring

  - #82: Remove setup.py and update poetry to 1.4.0 
  

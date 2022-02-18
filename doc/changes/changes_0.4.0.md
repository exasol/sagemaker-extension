# SageMaker Extension 0.4.0, released 2022-02-18

Code name: Removed Lua dependencies on the deployment

## Summary

This release removes Lua dependencies on the SageMaker-Extension deployment and 
provides users a simpler installation. In addition, continuous integration tests 
setup is completed, enabling us to have more reliable and maintainable releases. 
Furthermore, a developer guide is added, explaining how to build and test the project.


### Features

  - #34: Run real tests sequentially
  - #9: Setup ci-isolation for integration test 
  
### Bug Fixes

  - #56: Removed Lua dependency on deployment
  
### Documentation

  - #60: Added the developer guide
  
### Refactoring

  - #56: Used Click for the deployment cli script
    




  
    

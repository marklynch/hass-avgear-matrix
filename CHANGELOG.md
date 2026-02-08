# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-02-08
### Added
- Upgrade `hdmimatrix` library to `v0.1.0`
- Update the documentation page to point to github

## [0.1.0] - 2025-10-13
### Added
- Call power_on before trying to validate the connection
- Translations for spanish and french. 

### Changed
- Cleaned up the label handling between button and select to be consistent and log more cleanly	
- Simplified the naming of the AVGear Device to be AVGear Matrix and put the name and type in the model.	

### Removed
- Unused `strings.json`	
- remove unused internal variable in coordinator init.	

## [0.0.8] - 2025-10-13
### Changed
- Another fix on the audit log consistency

## [0.0.7] - 2025-10-13
### Added
- Call power_on before trying to read status during initial setup

### Changed
- Make the audit log names consistently use the device name
- Upgrade `hdmimatrix` library to `v0.0.6`

## [0.0.6] - 2025-10-13
### Added
- Send a `output_on` command with every routing change to ensure that routing works reliably
 
### Changed
- Upgrade `hdmimatrix` library to `v0.0.5`

## [0.0.5] - 2025-10-11
### Added
- Set internal state directly when changing a routing instead of waiting for full update.

### Changed
- Centralised matrix operations to the coordinator so that only one hdmimatrix is initialised
- Upgrade `hdmimatrix` library to `v0.0.4`

### Removed
- Removed locking as it was already handled in underlying [hdmimatrix](https://github.com/marklynch/hdmimatrix) code


## [0.0.4] - 2025-10-09
### Changed
- Fixed bug introduced with asyncio locking in 0.0.3

## [0.0.3] - 2025-10-09
### Added
- Buttons for power on and power off

### Changed
- Use lazy variable evaluation for logging
- Improve stability by adding asyncio locking

## [0.0.2] - 2025-08-14
### Added
- Read and display name, model and version

## [0.0.1] - 2025-08-11
### Added
- Basic functionality working - integration loads and can switch matrix inputs and outputs.
# Changelog

All notable changes to this project will be documented in this file.

## [1.1.2](https://github.com/stuartp44/haduco/compare/v1.1.1...v1.1.2) (2026-01-03)


### Bug Fixes

* simplify return values in find_box_addr and get_mac_address functions ([486e3ec](https://github.com/stuartp44/haduco/commit/486e3ec9390570d29404434775029fb4fad9f7a2))

## [1.1.1](https://github.com/stuartp44/haduco/compare/v1.1.0...v1.1.1) (2026-01-03)


### Bug Fixes

* enhance DucoPy initialization error handling for older board types ([da5fc16](https://github.com/stuartp44/haduco/commit/da5fc1618dc3fd94f74ab1162713a577bfdc5ba2))
* improve DucoPy client initialization and logging for detected board information ([e701c79](https://github.com/stuartp44/haduco/commit/e701c79a410174d5a13fd9882b3122272447b916))
* improve DucoPy initialization and logging for better error handling and board detection ([c8691a7](https://github.com/stuartp44/haduco/commit/c8691a7b2bdb093aa083d4a2204a51f61e0808b4))
* initialize DucoPy in executor to prevent blocking the event loop ([fd22a70](https://github.com/stuartp44/haduco/commit/fd22a70258b89bdb31f0478c2874170a1d640663))

## [1.1.0](https://github.com/stuartp44/haduco/compare/v1.0.5...v1.1.0) (2026-01-03)


### Features

* add debug verbosity option and improve logging in Ducobox integration ([13cb96f](https://github.com/stuartp44/haduco/commit/13cb96fc5fab3800221e9969fe5ae6258da5b6c0))


### Bug Fixes

* remove unnecessary blank lines in Ducobox config flow ([09fe2a8](https://github.com/stuartp44/haduco/commit/09fe2a8103dfb450782306802cb42f1c62a5f131))
* streamline debug verbosity option definition in OPTIONS_SCHEMA ([e8d33f8](https://github.com/stuartp44/haduco/commit/e8d33f82bb6ac3e9c4fdd06d8e313ddf6edf64da))

## [1.0.5](https://github.com/stuartp44/haduco/compare/v1.0.4...v1.0.5) (2026-01-03)


### Bug Fixes

* correct requirements format for ducopy dependency in manifest.json ([901497d](https://github.com/stuartp44/haduco/commit/901497dc4099dd71b9d3a40114be89e827b50d0a))

## [1.0.4](https://github.com/stuartp44/haduco/compare/v1.0.3...v1.0.4) (2026-01-03)


### Bug Fixes

* correct URL encoding in requirements for ducopy branch ([2e50d73](https://github.com/stuartp44/haduco/commit/2e50d731f88e935441c41c1e9927b615f45d6b47))

## [1.0.3](https://github.com/stuartp44/haduco/compare/v1.0.2...v1.0.3) (2026-01-03)


### Bug Fixes

* add missing zeroconf service for HTTP in manifest.json ([826edd5](https://github.com/stuartp44/haduco/commit/826edd53bc137fddcd852d41746453b866cb367c))

## [1.0.2](https://github.com/stuartp44/haduco/compare/v1.0.1...v1.0.2) (2026-01-03)


### Bug Fixes

* update requirements to use specific ducopy branch for enhanced functionality ([d9c55bb](https://github.com/stuartp44/haduco/commit/d9c55bbb1f75b6af10b8c3a81dda59d81cf5f728))

## [1.0.1](https://github.com/stuartp44/haduco/compare/v1.0.0...v1.0.1) (2025-12-30)


### Documentation

* update contributors [skip ci] ([859611f](https://github.com/stuartp44/haduco/commit/859611fdf112adf515c180dc3c90ef9a0599e2ff))

## 1.0.0 (2025-12-30)


### Features

* add project-specific instructions and style guide for documentation and code ([2724c24](https://github.com/stuartp44/haduco/commit/2724c24799d21765e3f127ea577065843c1dd205))
* add security policy and setup summary documentation ([142bf88](https://github.com/stuartp44/haduco/commit/142bf88743f037338c8ad2abf478eeeaddffdede))
* update documentation links in manifest and add config schema for integration ([6c50765](https://github.com/stuartp44/haduco/commit/6c50765729b833abce5221d38390336512615ccf))


### Bug Fixes

* reorder fields in manifest.json for consistency ([04e37a0](https://github.com/stuartp44/haduco/commit/04e37a0376933ed74cc44cb93b1959ea8c06491e))


### CI/CD

* **deps:** bump actions/github-script from 7 to 8 ([20ad300](https://github.com/stuartp44/haduco/commit/20ad3004ab3e90f1b85772fb84a702ed931d9694))
* **deps:** bump actions/setup-python from 5 to 6 ([3a04f28](https://github.com/stuartp44/haduco/commit/3a04f288def1ef080025cef4f992dc0bb73a48c7))
* **deps:** bump actions/stale from 9 to 10 ([24a6832](https://github.com/stuartp44/haduco/commit/24a683228637d0c2d1b65bdd069dc3cdd5e5623f))
* **deps:** bump akhilmhdh/contributors-readme-action ([caefcce](https://github.com/stuartp44/haduco/commit/caefccea52bd1ce4c7be6e1a0ea37df1c9e4c31a))
* **deps:** bump amannn/action-semantic-pull-request from 5 to 6 ([2f7d3b9](https://github.com/stuartp44/haduco/commit/2f7d3b9779a3b6e365d9a27d8a4258bca0734127))

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - Current

### Initial Release
- Integration with DUCO Ventilation & Sun Control systems
- Sensor platform support
- Select platform support
- Configuration flow
- Zeroconf discovery

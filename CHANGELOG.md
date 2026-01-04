# Changelog

All notable changes to this project will be documented in this file.

## [1.2.8](https://github.com/stuartp44/haduco/compare/v1.2.7...v1.2.8) (2026-01-04)


### Bug Fixes

* clean up DucoPy client on unload by ensuring proper closure of HTTP session ([96e4821](https://github.com/stuartp44/haduco/commit/96e48215a93508f855f0b07d47dc1ee7a729c635))
* correct log level mapping and enhance cleanup of DucoPy client on unload ([c771336](https://github.com/stuartp44/haduco/commit/c771336a123e7fd8ed20596c0997844c720b145d))
* enhance logging and increase sleep duration for device command processing in DucoboxModeSelect ([302474c](https://github.com/stuartp44/haduco/commit/302474cff42ccaa9d06496a44aa89ecfdc6c1718))
* enhance mock setup for DucoPy client and improve integration tests ([925924c](https://github.com/stuartp44/haduco/commit/925924c4be4886f7e8fbeb23e02b66bdf07fc543))
* improve error handling and data retrieval in DucoboxCoordinator ([69c1613](https://github.com/stuartp44/haduco/commit/69c161345e6acb94d8f6e204b7f3b56875c1ba24))
* remove unused import of MagicMock in test_init.py ([26c873e](https://github.com/stuartp44/haduco/commit/26c873e36ce7e486592dae7916c07d46665674fc))
* update IP address if changed for existing device configurations and improve error handling in data fetching ([a054eb3](https://github.com/stuartp44/haduco/commit/a054eb38028e6b093dae16d60bc30deab34b2ded))
* update type hints and improve documentation in coordinator.py; enhance commit instructions ([ad72e39](https://github.com/stuartp44/haduco/commit/ad72e3909229b06eadbb93776126b7aa28a1f16e))


### Documentation

* add instructions for running ruff checks and formatting before committing ([a27ae86](https://github.com/stuartp44/haduco/commit/a27ae863c5290997b64294cb89d68307143e7844))

## [1.2.7](https://github.com/stuartp44/haduco/compare/v1.2.6...v1.2.7) (2026-01-04)


### Bug Fixes

* handle both normalized and non-normalized formats in find_box_addr function ([e96616e](https://github.com/stuartp44/haduco/commit/e96616eae5d224f11b6d8260796675d9db90215f))

## [1.2.6](https://github.com/stuartp44/haduco/compare/v1.2.5...v1.2.6) (2026-01-04)


### Bug Fixes

* improve action retrieval and address handling in select and sensor components ([0b56654](https://github.com/stuartp44/haduco/commit/0b56654d46f52b69a343d47274c2e01e8aa48a61))

## [1.2.5](https://github.com/stuartp44/haduco/compare/v1.2.4...v1.2.5) (2026-01-04)


### Bug Fixes

* enhance discovery process to prefer HTTPS for modern Connectivity Boards ([bccbfa3](https://github.com/stuartp44/haduco/commit/bccbfa3d54c5051aef44667e53695f7900523342))
* prefer HTTPS for modern Connectivity Boards during discovery process ([f4f5e6f](https://github.com/stuartp44/haduco/commit/f4f5e6f54b62bb01c1842d2313f721080a4501aa))

## [1.2.4](https://github.com/stuartp44/haduco/compare/v1.2.3...v1.2.4) (2026-01-04)


### Bug Fixes

* update device description to include board type in confirmation message ([3d63ba8](https://github.com/stuartp44/haduco/commit/3d63ba85658b4c163c387b0e5d6d6ad88663dd06))
* update flow title format in English translation ([4204938](https://github.com/stuartp44/haduco/commit/42049384d52c08ef11f700dbe107a633ac9ae095))

## [1.2.3](https://github.com/stuartp44/haduco/compare/v1.2.2...v1.2.3) (2026-01-04)


### Bug Fixes

* add debug logging for existing entry checks in config flow ([c019ca5](https://github.com/stuartp44/haduco/commit/c019ca5dd98ac3cca7519c09f06d44c882f6b679))

## [1.2.2](https://github.com/stuartp44/haduco/compare/v1.2.1...v1.2.2) (2026-01-04)


### Bug Fixes

* enhance logging in discovery process for better debugging ([c126c36](https://github.com/stuartp44/haduco/commit/c126c3671e34cb7e0401726b5169d90222a34f27))

## [1.2.1](https://github.com/stuartp44/haduco/compare/v1.2.0...v1.2.1) (2026-01-04)


### Bug Fixes

* update valid discovery names to include 'duco[' for improved device detection ([aa58289](https://github.com/stuartp44/haduco/commit/aa582895f475b98a2417050a24b3280fdc51683b))

## [1.2.0](https://github.com/stuartp44/haduco/compare/v1.1.3...v1.2.0) (2026-01-04)


### Features

* enhance Zeroconf discovery logging and update manifest for service types ([440fe7d](https://github.com/stuartp44/haduco/commit/440fe7d2f9e84cae0dd2cfe74e5da02654570eee))


### Bug Fixes

* improve logging format in async_step_zeroconf for better readability ([78cc228](https://github.com/stuartp44/haduco/commit/78cc228499456672d2530ebd399bb8a379755776))

## [1.1.3](https://github.com/stuartp44/haduco/compare/v1.1.2...v1.1.3) (2026-01-04)


### Bug Fixes

* refine MAC address retrieval and improve node ID handling in select.py ([4c581c0](https://github.com/stuartp44/haduco/commit/4c581c0a3661fa88b94726ec1c615a95282f9c0c))

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

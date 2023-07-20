# Matrix-PyPI: Overview

**Matrix-PyPI** is a distributed caching proxy Python Package Index (PyPI) that leverages Matrix as a distributed trust layer and IPFS as a distributed data store.

### Usage Example

Matrix-PyPI operates as a transparent proxy for installing Python packages with `pip`. Specifying a local Matrix-PyPI proxy as your package index lets you pull packages as you normally would, with the added efficiency and reliability of a caching proxy.

```shell
# Launch the matrix-pypi docker container
docker run -p 8080:8080 matrixpypi/matrixpypi:latest

# Use Matrix-PyPI as your package index
pip install --index-url=http://localhost:8080/simple/ some-package
```

### Enhanced Package Delivery

Matrix facilitates package integrity verification. For every package, a dedicated Matrix room exists where maintainers and trusted mirrors publish package attestations and verify package authenticity. When a user requests a package, the system checks the local cache or the distributed IPFS network. If unavailable, the system retrieves the package from PyPI, stores it locally and on IPFS, and serves it to the user.

### Trust Verification and Security

Before serving a cached package, the system checks the package's attestation in the corresponding Matrix room. If the attestation matches the known metadata, the package is delivered. This process ensures the integrity of the package in a distributed setting. Mechanisms are in place to identify and remove fraudulent attestations, provided there's at least one honest participant in a Matrix room.

### Flexibility and Adaptability

Matrix-PyPI provides a modular API for implementing storage backends, enabling users to implement their own solutions. A default IPFS implementation is provided.

In essence, **Matrix-PyPI** offers an efficient, secure, and user-friendly approach to Python package management. Its resilient architecture leverages the benefits of Matrix and IPFS to improve the Python package distribution ecosystem.

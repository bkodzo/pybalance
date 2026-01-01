# Contributing to PyBalance

Thank you for your interest in contributing to PyBalance! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/LoadBalancer.git
   cd LoadBalancer
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. **Ensure Python 3.7+ is installed**:
   ```bash
   python3 --version
   ```

2. **Install dependencies** (optional, for C++ extension):
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Set up Docker** (for backend servers):
   ```bash
   docker-compose up -d
   ```

4. **Run the load balancer**:
   ```bash
   python3 main.py
   ```

## Code Style

- **Write docstrings**: Document functions and classes
- **Keep it simple**: Prefer clarity over cleverness


## Testing

Before submitting a pull request:

1. **Test your changes**:
   ```bash
   ./test_algorithms.sh
   ./test_now.sh
   ```

2. **Run load tests** (if applicable):
   ```bash
   python3 load_test.py
   ```

3. **Test health monitoring**:
   - Stop a backend: `docker-compose stop backend1`
   - Verify it's detected as dead
   - Restart it: `docker-compose start backend1`
   - Verify it's detected as alive

## Pull Request Process

1. **Update documentation** if you add features or change behavior
2. **Add tests** if you add new functionality
3. **Update README.md** if you change setup or usage
4. **Write clear commit messages**:
   ```
   Add feature: SSL/TLS termination
   
   - Implement SSL certificate loading
   - Add HTTPS support to proxy engine
   - Update configuration for SSL settings
   ```

5. **Submit pull request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots or examples if applicable

## Areas for Contribution

### High Priority

- **SSL/TLS Termination**: Handle HTTPS connections
- **HTTP/2 Support**: Modern protocol support
- **Prometheus Metrics**: Standard metrics format
- **Configuration File**: YAML/JSON config support
- **Kubernetes Manifests**: K8s deployment examples

### Medium Priority

- **Rate Limiting**: Protect backends from overload
- **Sticky Sessions**: Cookie-based session affinity
- **Advanced Health Checks**: HTTP endpoint checks
- **Load Balancing Policies**: More sophisticated algorithms
- **Monitoring Dashboard**: Web UI for metrics

### Low Priority

- **Performance Optimizations**: Further speed improvements
- **Documentation**: Improve clarity and examples
- **Test Coverage**: Add more test cases
- **Code Refactoring**: Improve code organization

## Code Structure

### Core Modules

- `main.py`: Entry point, orchestrates components
- `router.py`: Request routing logic
- `proxy.py`: Async proxy engine
- `health_monitor.py`: Background health monitoring
- `metrics.py`: Metrics collection
- `config.py`: Configuration settings

### Adding a New Routing Algorithm

1. **Add to enum** in `router.py`:
   ```python
   class RoutingAlgorithm(Enum):
       # ... existing algorithms
       NEW_ALGORITHM = "new_algorithm"
   ```

2. **Implement the algorithm**:
   ```python
   def _new_algorithm(self, servers: List[Server], ...) -> Server:
       # Your implementation
       pass
   ```

3. **Add to select_server**:
   ```python
   elif self.algorithm == RoutingAlgorithm.NEW_ALGORITHM:
       return self._new_algorithm(alive_servers, ...)
   ```

4. **Update documentation**:
   - Add to README.md
   - Add to ROUTING_ALGORITHMS.md

### Adding a New Feature

1. **Design the feature**: Consider architecture and impact
2. **Update relevant modules**: Keep changes focused
3. **Add tests**: Ensure it works correctly
4. **Update documentation**: README, ARCHITECTURE.md, etc.
5. **Update config.py**: If configuration is needed

## Questions?

- Open an issue for bugs or feature requests
- Ask questions in issue discussions
- Review existing code for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyBalance!


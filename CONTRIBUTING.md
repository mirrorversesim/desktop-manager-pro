# Contributing to Desktop Manager Pro

Thank you for your interest in contributing to Desktop Manager Pro! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/yourusername/desktop-manager-pro/issues) page
- Include detailed information about your system (Windows version, Python version)
- Provide steps to reproduce the issue
- Include relevant log files from the `logs/` directory

### Suggesting Features
- Use the [GitHub Issues](https://github.com/yourusername/desktop-manager-pro/issues) page
- Clearly describe the feature and its benefits
- Consider implementation complexity and user impact

### Code Contributions
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** your changes thoroughly
5. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- Git for Windows
- Administrator privileges (for testing autostart features)

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/desktop-manager-pro.git
cd desktop-manager-pro

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Testing
- Test on different Windows versions if possible
- Test with different Python versions (3.8+)
- Test both portable and installer versions
- Test system tray functionality
- Test autostart features

## 📝 Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Example
```python
def move_window_to_monitor(window_handle: int, monitor_index: int) -> bool:
    """
    Move a window to a specific monitor.
    
    Args:
        window_handle: Handle of the window to move
        monitor_index: Index of the target monitor (0-based)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Implementation here
        return True
    except Exception as e:
        logger.error(f"Failed to move window: {e}")
        return False
```

### UI Code
- Follow tkinter best practices
- Use consistent naming conventions
- Implement proper error handling
- Ensure accessibility features

### Configuration Files
- Use JSON format for configuration files
- Include comments for complex configurations
- Validate configuration on load
- Provide sensible defaults

## 🏗️ Project Structure

### Core Modules
- `src/core/` - Core functionality (event monitoring, window management)
- `src/ui/` - User interface components
- `src/rules/` - Rule engine and automation
- `src/utils/` - Utility functions and helpers

### Adding New Features
1. **Core Logic**: Add to appropriate module in `src/core/`
2. **UI Components**: Add to `src/ui/` with proper integration
3. **Configuration**: Update configuration files in `config/`
4. **Documentation**: Update README.md and relevant docs
5. **Tests**: Add tests to `tests/` directory

### Adding New Rules
1. **Action Types**: Add to `src/rules/actions.py`
2. **Validation**: Update `src/rules/config.py`
3. **Documentation**: Update rule documentation
4. **Examples**: Add example rules to configuration

## 🧪 Testing Guidelines

### Manual Testing
- Test all major features
- Test edge cases and error conditions
- Test on different Windows versions
- Test with different user permissions

### Automated Testing
- Add unit tests for new functions
- Add integration tests for complex features
- Test configuration loading and validation
- Test error handling and recovery

### Performance Testing
- Monitor resource usage
- Test with many windows open
- Test long-running operation
- Verify minimal impact on system performance

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints
- Document complex algorithms
- Add inline comments for tricky code

### User Documentation
- Update README.md for new features
- Add usage examples
- Update configuration documentation
- Create tutorials for complex features

### API Documentation
- Document public APIs
- Include usage examples
- Document parameter types and return values
- Add deprecation notices when needed

## 🔄 Pull Request Process

### Before Submitting
1. **Test** your changes thoroughly
2. **Update** documentation as needed
3. **Check** code style and formatting
4. **Verify** no breaking changes (unless intended)
5. **Update** CHANGELOG.md if needed

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested portable version
- [ ] Tested installer version
- [ ] Tested system tray functionality

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
- [ ] CHANGELOG.md updated
```

## 🏷️ Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

## 📄 License

By contributing to Desktop Manager Pro, you agree that your contributions will be licensed under the MIT License.

## 🆘 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check README.md and inline documentation
- **Code Examples**: Look at existing code for patterns

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page
- Project documentation

---

**Thank you for contributing to Desktop Manager Pro!** 🎉

*Your contributions help make Windows desktop management better for everyone.* 
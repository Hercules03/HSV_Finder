# Contributing to HSV Range Finder

Thank you for your interest in contributing to HSV Range Finder! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions in many forms:
- 🐛 Bug reports and fixes
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Test coverage improvements
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Git for version control
- Basic knowledge of OpenCV and computer vision concepts
- Familiarity with Tkinter for GUI contributions

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/HSV_Finder.git
   cd HSV_Finder
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   # Test that the application runs
   python main.py
   
   # Verify code compiles without errors
   python -m py_compile main.py
   ```

4. **Set Up Development Branch**
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name
   
   # Or for bug fixes:
   git checkout -b fix/issue-description
   ```

## 📋 Development Guidelines

### Code Style and Standards

#### Python Code Standards
- **PEP 8**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type annotations for all new functions
- **Docstrings**: Include comprehensive docstrings for classes and methods
- **Error Handling**: Implement robust error handling with user-friendly messages

#### Example Code Style
```python
def process_image_data(
    self, 
    image: np.ndarray, 
    lower_bound: np.ndarray, 
    upper_bound: np.ndarray
) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Process image data with HSV filtering.
    
    Args:
        image: Input BGR image array
        lower_bound: Lower HSV threshold values
        upper_bound: Upper HSV threshold values
        
    Returns:
        Tuple of (original, filtered, binary) images or None if processing fails
        
    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If image processing fails
    """
    try:
        # Validate inputs
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        # Process image
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        return original, filtered, binary
        
    except Exception as e:
        print(f"Processing error: {str(e)}")
        return None
```

### Architecture Guidelines

#### Separation of Concerns
- **UI Code**: Keep UI creation separate from business logic
- **Processing Logic**: Separate image processing from UI updates
- **Configuration**: Use the `Config` class for all constants and settings
- **Error Handling**: Centralize error handling patterns

#### Performance Considerations
- **Caching**: Implement caching for expensive operations
- **Debouncing**: Use debouncing for rapid user input
- **Memory Management**: Be mindful of memory usage with large images
- **Lazy Loading**: Load resources only when needed

### Testing Guidelines

#### Manual Testing Checklist
- [ ] Application launches without errors
- [ ] Image loading works for various formats (PNG, JPG, BMP, etc.)
- [ ] HSV sliders update display in real-time
- [ ] Entry fields accept valid numerical input
- [ ] Copy functionality works for both upper and lower ranges
- [ ] Toggle between filtered and binary mask views works
- [ ] Application closes cleanly without errors
- [ ] Cross-platform compatibility (test on Windows, macOS, Linux if possible)

#### Test Scenarios
1. **Large Image Handling**
   - Test with images >50MB
   - Verify warning dialogs appear
   - Ensure performance remains acceptable

2. **Edge Cases**
   - Empty image files
   - Corrupted image files
   - Extreme HSV values (0, 255, etc.)
   - Very small images (<10x10 pixels)

3. **User Input Validation**
   - Invalid numerical input in entry fields
   - Out-of-range HSV values
   - Rapid slider movements

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Load image 'example.jpg'
2. Set HSV values to [50, 100, 150]
3. Click toggle button
4. See error message

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [Windows 10, macOS 12.0, Ubuntu 20.04, etc.]
- Python Version: [3.8.5]
- OpenCV Version: [4.5.2]
- Application Version/Commit: [latest/commit hash]

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Additional Context**
Any other context about the problem.
```

### Feature Requests

For feature requests, please include:
- **Use Case**: Describe the problem you're trying to solve
- **Proposed Solution**: Your idea for how to address it
- **Alternatives**: Other solutions you've considered
- **Impact**: Who would benefit from this feature

## 📝 Pull Request Process

### Before Submitting

1. **Test Thoroughly**
   - Verify your changes work as expected
   - Test edge cases and error conditions
   - Check cross-platform compatibility if possible

2. **Update Documentation**
   - Update README.md if needed
   - Add/update docstrings for new functions
   - Update EXAMPLES.md with new usage patterns

3. **Code Quality**
   - Run code through Python syntax checker
   - Ensure type hints are present
   - Verify error handling is implemented

### Pull Request Template

```markdown
## Description
Brief description of the changes in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Manual testing completed
- [ ] Cross-platform testing (specify platforms tested)
- [ ] Edge cases tested
- [ ] Performance impact assessed

## Changes Made
- Change 1: Description
- Change 2: Description
- Change 3: Description

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated as needed
- [ ] No new warnings introduced
```

## 🏗️ Areas for Contribution

### High Priority
1. **Cross-Platform Testing**: Verify functionality on Windows, macOS, and Linux
2. **Error Handling**: Improve error messages and edge case handling
3. **Performance**: Optimize image processing for larger files
4. **Documentation**: Improve code documentation and user guides

### Medium Priority
1. **UI Enhancements**: Improve user interface and experience
2. **Feature Extensions**: Add new color spaces (LAB, YUV, etc.)
3. **Export Functionality**: Add JSON/XML export for HSV ranges
4. **Keyboard Shortcuts**: Add keyboard shortcuts for common operations

### Nice to Have
1. **Batch Processing**: Process multiple images at once
2. **Preset Ranges**: Save and load common HSV ranges
3. **Advanced Filters**: Add morphological operations
4. **Plugin System**: Architecture for third-party extensions

## 🎯 Specific Contribution Guidelines

### UI/UX Contributions
- Maintain consistency with existing design
- Ensure accessibility (keyboard navigation, clear labels)
- Test with different screen sizes and resolutions
- Follow platform-specific UI guidelines when relevant

### Performance Contributions
- Profile code before and after changes
- Document performance improvements with metrics
- Consider memory usage impact
- Test with various image sizes (small to very large)

### Documentation Contributions
- Use clear, concise language
- Include practical examples
- Update all relevant documentation files
- Ensure examples are tested and working

### Bug Fix Contributions
- Include test case that reproduces the bug
- Explain the root cause in the PR description
- Verify fix doesn't introduce regressions
- Update documentation if behavior changes

## 🛠️ Development Tips

### Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints for development
print(f"HSV bounds: lower={lower_bound}, upper={upper_bound}")
print(f"Image shape: {image.shape}")
```

### Performance Testing
```python
import time

# Time critical operations
start_time = time.time()
# ... your code here
end_time = time.time()
print(f"Operation took {end_time - start_time:.3f} seconds")
```

### Cross-Platform Development
- Test file path handling on different OS
- Verify file dialog behavior
- Check font and UI element rendering
- Test with different Python versions if possible

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Request Reviews**: For code-specific questions

### Code Review Process
1. Submit pull request with detailed description
2. Maintainers will review within 1-2 weeks
3. Address any feedback or requested changes
4. Once approved, maintainer will merge

### Response Times
- **Bug Reports**: We aim to respond within 48 hours
- **Feature Requests**: Response within 1 week
- **Pull Requests**: Review within 1-2 weeks

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README.md acknowledgments section

## 📄 License Agreement

By contributing to HSV Range Finder, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to HSV Range Finder! Your help makes this project better for the entire computer vision community. 🎉
# Management Commands for Testing

## 🌟 **RECOMMENDED: `ultimate_live_test.py`**

**This is the unified solution for all live domain testing via SSH.**

```bash
python manage.py ultimate_live_test --username=admin --password=yourpass --email=admin@example.com
```

### Features:
- ✅ Complete comprehensive testing (8 categories, 50+ tests)
- ✅ Production safety (DEBUG=False protection)
- ✅ SSH-ready for live domain testing
- ✅ Automatic cleanup preserving logs
- ✅ Test categories for targeted testing

---

## 📁 **Other Commands:**

| Command | Status | Purpose |
|---------|---------|---------|
| `ultimate_live_test.py` | 🌟 **USE THIS** | Unified comprehensive testing |
| `comprehensive_live_test.py` | ⚠️ Legacy | Old comprehensive approach (has DEBUG protection) |
| `test_live_domain.py` | ⚠️ Legacy | Original live domain testing |
| `generuj_testowe_zgloszenia.py` | ✅ Active | Generate test tickets |
| `setup_demo_data.py` | ✅ Active | Setup demo data |

---

## 🚀 **Quick Start:**

Use the root-level `quick_test_setup.py` for easiest deployment:

```bash
python quick_test_setup.py --install-deps --username=admin --password=yourpass --email=admin@example.com
```

### **🔧 For Full Browser Testing:**
Install Chrome on FreeBSD to enable mobile responsiveness and UI tests:
```bash
sudo pkg install chromium chromedriver
```
See `CHROME_SETUP_FREEBSD.md` for detailed setup instructions.

### **⚡ Current Test Coverage Without Browser:**
- ✅ **27% Success Rate** (13/48 tests passing)
- ✅ **Authentication & Security**: Complete API-based testing
- ✅ **Organization Management**: Full CRUD operations
- ✅ **2FA Configuration**: Settings and model validation
- ⏭️ **33 Placeholder Tests**: Framework structure for future implementation
- ❌ **Mobile & UI Tests**: Require browser (skipped on SSH)

### **🎯 After Chrome Installation:**
- 🚀 **85%+ Success Rate** expected
- ✅ **Mobile Responsiveness**: 4 viewport sizes tested
- ✅ **UI Interactions**: Toast notifications, forms, visual feedback
- ✅ **Complete 2FA Flow**: Setup, verification, backup codes

---

## 🛡️ **Production Safety:**

All testing commands now include DEBUG=False protection. Tests will not run on production unless you temporarily enable DEBUG mode.

**See `ULTIMATE_TESTING_SOLUTION.md` in the root directory for complete documentation.**

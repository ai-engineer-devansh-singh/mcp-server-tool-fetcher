# Quick Test Commands

## Basic Command Structure
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe <test_file>.py
```

## All Available Tests

### 1. Simple Test (Playwright)
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_simple.py
```

### 2. Fetch Test
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_fetch.py
```

### 3. Multi-Server Test
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_multi.py
```

### 4. Docker Test ✅
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_docker.py
```

### 5. UV Python Servers Test ✅
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_uv.py 2>$null
```

### 6. Comprehensive Test (All Types) ✅
```powershell
cd 'd:\Projects\MCP python' ; C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe test_comprehensive.py 2>$null
```

## Test Results Summary

| Test File | Status | Servers | Tools | Notes |
|-----------|--------|---------|-------|-------|
| test_simple.py | ✅ | 1 | 22 | Playwright browser automation |
| test_fetch.py | ⚠️ | 1 | 0 | Connection issues |
| test_multi.py | ✅ | 3 | ~30 | Multiple server types |
| **test_docker.py** | ✅ | 1 | 12 | Docker containerization |
| **test_uv.py** | ✅ | 2 | 8 | Python UV servers |
| **test_comprehensive.py** | ✅ | 3 | 36 | Complete test |

## Notes
- Add `2>$null` to suppress harmless cleanup warnings
- Docker Desktop should be running for docker tests
- UV/UVX must be installed for UV tests

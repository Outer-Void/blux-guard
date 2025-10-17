#!/usr/bin/env python3
"""
BLUX Guard Module Inspector
Prints current status of sensors, decisions engine, anti-tamper modules
"""

import importlib
import inspect
import json
from pathlib import Path

def inspect_module(module_name, class_name=None):
    """Inspect a specific module and its components"""
    print(f"\n🔍 {module_name.upper()}")
    print("=" * 40)
    
    try:
        module = importlib.import_module(f"blux_modules.{module_name}")
        
        # List available classes
        classes = [cls for name, cls in inspect.getmembers(module, inspect.isclass) 
                  if cls.__module__ == f"blux_modules.{module_name}"]
        
        print(f"Available classes: {[cls.__name__ for cls in classes]}")
        
        if class_name:
            # Inspect specific class
            target_class = getattr(module, class_name)
            print(f"\nClass: {class_name}")
            print(f"Methods: {[m for m in dir(target_class) if not m.startswith('_')]}")
            
            # Try to create instance and get status
            try:
                instance = target_class()
                if hasattr(instance, 'get_status'):
                    status = instance.get_status()
                    print(f"Status: {json.dumps(status, indent=2)}")
            except Exception as e:
                print(f"Could not instantiate: {e}")
                
    except ImportError as e:
        print(f"❌ Module not found: {e}")
    except Exception as e:
        print(f"❌ Inspection error: {e}")

def main():
    print("BLUX Guard Module Inspector")
    print("===========================")
    
    modules_to_check = [
        ("security_engine", "SecurityEngine"),
        ("sensor_manager", "SensorManager"), 
        ("decision_engine", "DecisionEngine"),
        ("anti_tamper", "AntiTamper")
    ]
    
    for module_name, class_name in modules_to_check:
        inspect_module(module_name, class_name)
    
    # Check config files
    print(f"\n📁 CONFIGURATION FILES")
    print("=" * 40)
    for config_file in ["rules/rules.json", "config/auth.json"]:
        path = Path(config_file)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                print(f"✅ {config_file}: {len(data)} config sections")
            except Exception as e:
                print(f"❌ {config_file}: Invalid JSON - {e}")
        else:
            print(f"⚠️  {config_file}: Missing")

if __name__ == "__main__":
    main()

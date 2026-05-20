#!/usr/bin/env python3
"""Quick test to verify setup and generate dataset"""

import sys
import os

# Test 1: Check Python
print("✅ Python version:", sys.version.split()[0])

# Test 2: Check directory
print("✅ Working directory:", os.getcwd())

# Test 3: Try importing key libraries
try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy not found: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas not found: {e}")
    sys.exit(1)

try:
    from sklearn.preprocessing import StandardScaler
    print("✅ Scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ Scikit-learn not found: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Running data generator...")
print("="*60 + "\n")

# Run data generator
from data_generator import generate_student_data
from pathlib import Path

data_dir = Path(__file__).parent / 'data' / 'raw'
data_dir.mkdir(parents=True, exist_ok=True)

df = generate_student_data(n_students=800)
output_path = data_dir / 'student_data.csv'
df.to_csv(output_path, index=False)

print(f"\n✅ Dataset saved to: {output_path}")
print(f"   Shape: {df.shape}")
print(f"   Placed: {df['Placed'].sum()} ({100*df['Placed'].mean():.1f}%)")

print("\n" + "="*60)
print("✅ TEST PASSED - Ready to run preprocessing!")
print("="*60)

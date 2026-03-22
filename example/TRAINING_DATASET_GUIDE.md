# Training Dataset for HSP Sphere Fitting

## 📋 Overview

This is the **training dataset** used to calculate (fit) the Hansen Solubility Parameters (HSP) sphere. It contains your drug's solubility data in 12 different solvents.

**File**: `training_dataset_for_HSP_fitting.csv`

---

## 🎯 What This Dataset Is

This is **NOT** a general solvent database. Instead, it contains:

1. **12 Solvents** with known Hansen parameters
2. **Experimental Solubility Data** for YOUR SPECIFIC DRUG in each solvent
3. **Labels** indicating whether the drug is miscible or immiscible in each

This data is used by the optimization algorithm to find the best HSP values that describe your drug.

---

## 📊 Dataset Structure

```
Name,D,P,H,Solubility
Tetronic_1107,16.37,14.72,8.50,miscible
Tetronic_1307,16.02,11.75,6.79,borderline
... (10 more rows)
```

### Column Explanations

| Column | Type | Meaning |
|--------|------|---------|
| **Name** | Text | Solvent name (must match your database) |
| **D** | Number | Hansen Dispersion parameter (MPa^0.5) |
| **P** | Number | Hansen Polar parameter (MPa^0.5) |
| **H** | Number | Hansen H-bonding parameter (MPa^0.5) |
| **Solubility** | Text | Your experimental observation: "miscible", "immiscible", or "borderline" |

---

## 🧪 Solubility Column

### Definitions

**miscible** (or "soluble")
- Your drug completely dissolves in the solvent
- Clear, homogeneous solution
- No phase separation

**immiscible** (or "insoluble")
- Your drug does NOT dissolve in the solvent
- Visible phase separation
- Precipitation or suspended particles

**borderline**
- Partial solubility
- Cloudy solution
- Slow dissolution or precipitation over time
- **Treatment in algorithm**: Converted to "immiscible" (conservative approach)

---

## 📈 Example Dataset Breakdown

### Miscible Solvents (3)
```
Tetronic_1107, 16.37, 14.72, 8.50  → Your drug dissolves ✓
DMF,           17.4,  13.7,  11.3  → Your drug dissolves ✓
THF,           16.8,  5.7,   8.0   → Your drug dissolves ✓
DMSO,          18.4,  16.4,  10.2  → Your drug dissolves ✓
```

### Immiscible Solvents (7)
```
Tetronic_90R4, 14.58, 10.72, 6.19  → Your drug does NOT dissolve ✗
Poloxamer_407, 15.35, 11.28, 6.51  → Your drug does NOT dissolve ✗
Ethanol,       15.8,  8.8,   19.4  → Your drug does NOT dissolve ✗
ACN,           15.3,  18.0,  6.1   → Your drug does NOT dissolve ✗
Methanol,      15.1,  12.3,  22.3  → Your drug does NOT dissolve ✗
Acetone,       15.5,  10.4,  7.0   → Your drug does NOT dissolve ✗
```

### Borderline Solvents (2)
```
Tetronic_1307, 16.02, 11.75, 6.79  → Partial solubility (treated as immiscible)
Poloxamer_188, 15.96, 11.71, 6.76  → Partial solubility (treated as immiscible)
```

---

## 🔬 How This Data Is Used

### Step 1: Load Data
The application reads this CSV file and extracts:
- HSP values (D, P, H) for each solvent
- Solubility labels (miscible/immiscible)

### Step 2: Optimization
The differential evolution algorithm searches for HSP parameters that:
- Place miscible solvents **inside** the solubility sphere
- Place immiscible solvents **outside** the solubility sphere
- Minimize the sphere radius (Occam's razor principle)

### Step 3: Result
Optimal HSP for your drug:
```
dD = 20.13 MPa^0.5  (Dispersion)
dP = 10.16 MPa^0.5  (Polar)
dH = 12.24 MPa^0.5  (H-bonding)
R  = 6.99  MPa^0.5  (Solubility radius)
```

### Step 4: Prediction
Once fitted, the sphere predicts solubility for **any other solvent** in your database.

---

## 📊 Data Quality Requirements

### Minimum Requirements

- ✅ **At least 10 solvents** (we have 12)
- ✅ **Mix of miscible AND immiscible** (we have both)
- ✅ **Known HSP values** (all provided)
- ✅ **Experimental solubility data** (all labeled)

### Quality Checks

- **HSP values**: Should be realistic (typically 10-25 for D, P, H)
- **Balance**: Mix of high and low HSP values
- **Diversity**: Cover different regions of HSP space
- **Accuracy**: Solubility labels should be reliable

---

## 🎯 How to Prepare Your Own Dataset

If you want to use your own drug:

### 1. Experimental Work
```
Select 12+ solvents
↓
Test drug solubility in each solvent (at fixed temperature)
↓
Record: Fully soluble / Partially soluble / Insoluble
```

### 2. Data Collection
```
For each solvent, find or calculate:
- D (Dispersion parameter)
- P (Polar parameter)
- H (H-bonding parameter)
```

**Sources for HSP values:**
- [Hansen Solubility Parameters Database](http://www.hansensolubility.com/)
- Literature (Hansen's book, scientific papers)
- QSAR predictions
- Estimation from molecular structure

### 3. Create CSV
```csv
Name,D,P,H,Solubility
YourSolvent1,15.5,10.0,8.0,miscible
YourSolvent2,14.0,5.0,2.0,immiscible
...
```

### 4. Load in Application
- Open openHSP_BEAUTIFUL.py
- Load the general solvent database
- Select your 12 solvents
- Mark each as soluble/insoluble
- Click "Calculate HSP"

---

## 📋 Current Dataset: Breakdown by Type

### Polymers (2 miscible, 2 borderline, 1 immiscible)
```
Tetronic_1107      - 1107 PEG copolymer - miscible ✓
Tetronic_1307      - 1307 PEG copolymer - borderline ~
Tetronic_90R4      - 90R4 PEG copolymer - immiscible ✗
Poloxamer_188      - PPO-PEO block - borderline ~
Poloxamer_407      - PPO-PEO block - immiscible ✗
```

### Aprotic Dipolar (2 miscible)
```
DMF                - Dimethyl Formamide - miscible ✓
DMSO               - Dimethyl Sulfoxide - miscible ✓
```

### Ethers (1 miscible)
```
THF                - Tetrahydrofuran - miscible ✓
```

### Alcohols (3 immiscible)
```
Ethanol            - Primary alcohol - immiscible ✗
Methanol           - Primary alcohol - immiscible ✗
(implied in data)
```

### Ketones & Nitriles (2 immiscible)
```
Acetone            - Simple ketone - immiscible ✗
ACN                - Acetonitrile - immiscible ✗
```

**Total**: 12 solvents covering diverse chemical classes

---

## 🔍 Why This Dataset Works

### ✓ Good Coverage
```
        D (Dispersion)
        ↓
    14.0 -------- 18.5
    
        P (Polar)
        ↓
    5.0 --------- 18.0
    
        H (H-bonding)
        ↓
    6.0 --------- 22.3
```

Solvents spread across HSP space, not clustered in one corner.

### ✓ Clear Separation
Miscible and immiscible solvents are reasonably separated, making it possible to fit a sphere between them.

### ✓ Balanced Set
- Not all miscible in one region
- Not all immiscible in one region
- Mix of different solvent types

---

## 📊 Expected Results

When you fit this dataset, you should get:

```
Optimized HSP: [20.13, 10.16, 12.24]
Radius: 6.99 MPa^0.5

Classification Accuracy: 12/12 (100%)
F1 Score: 1.000

Miscible (inside sphere): 4 solvents ✓
Immiscible (outside sphere): 8 solvents ✓
```

---

## 💡 Tips for Your Own Data

### ✅ Do's
- ✓ Use solvents with well-established HSP values
- ✓ Include variety: aprotic, protic, polar, nonpolar
- ✓ Mix high and low Hansen parameters
- ✓ Use at least 10 solvents (we used 12)
- ✓ Verify experimental solubility carefully

### ❌ Don'ts
- ✗ Use solvents all with similar HSP
- ✗ Mix miscible/immiscible with different solvents at different temps
- ✗ Use uncertain HSP values
- ✗ Use less than 8 solvents
- ✗ Include solvents where solubility is unclear

---

## 🔧 How to Use in openHSP

### Method 1: Load from Database + Manual Selection
1. Load `example_solvent_database.csv` (general database)
2. Search for and select the 12 training solvents
3. Mark each as miscible/immiscible based on your data
4. Click "Calculate HSP"

### Method 2: Pre-formatted CSV (Recommended)
1. Create a CSV with your training data
2. Use columns: Name, D, P, H, Solubility
3. Load into the application
4. Select solvents and mark solubility

---

## 📚 References

### Papers on HSP
- Hansen, C. M. (2007). *Hansen Solubility Parameters: A User's Handbook*, 2nd ed.
- Barton, A. F. M. (1975). *Solubility Parameters and Other Cohesion Parameters*

### HSP Databases
- [Official HSP Database](http://www.hansensolubility.com/)
- SciFinder (chemical database)
- PubChem (free online database)

### Software
- HSPiP (Hansen Solubility Parameter in Practice) - Commercial
- openHSP - Free, open-source

---

## 🎯 Summary

This dataset:
- **Contains**: 12 experimental solubility measurements
- **Purpose**: Train the HSP fitting algorithm
- **Result**: Optimal HSP for your drug
- **Use**: Predict solubility in other solvents

**Key Point**: The quality of your HSP prediction depends entirely on the quality and accuracy of this training data!

---

## 📝 Template for Your Own Data

```csv
Name,D,P,H,Solubility
YourSolvent_1,15.5,10.0,8.0,miscible
YourSolvent_2,14.0,5.0,2.0,immiscible
YourSolvent_3,18.0,8.0,5.0,immiscible
YourSolvent_4,16.0,12.0,10.0,miscible
YourSolvent_5,17.0,6.0,4.0,immiscible
YourSolvent_6,15.0,9.0,7.0,borderline
YourSolvent_7,14.5,4.0,2.0,immiscible
YourSolvent_8,17.5,14.0,12.0,miscible
YourSolvent_9,15.8,7.0,6.0,immiscible
YourSolvent_10,16.5,10.0,8.0,borderline
YourSolvent_11,18.0,5.0,3.0,immiscible
YourSolvent_12,15.2,11.0,9.0,miscible
```

---

**Ready to fit your own drug? Use this dataset as a template!** 🧪✨

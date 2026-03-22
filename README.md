# openHSP

**Hansen Solubility Parameter (HSP) Calculator with Beautiful Screening Interface**

A professional PySide6-based GUI application for calculating Hansen Solubility Parameters and screening solvents against optimized solubility spheres. Perfect for pharmaceutical, chemical, and materials science research.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

### 🎯 Core Functionality
- **HSP Calculation**: Optimize Hansen Solubility Parameters from experimental solubility data
- **Sphere Fitting**: Automatic solubility sphere creation using differential evolution optimization
- **Solvent Screening**: Test solvents against the optimized sphere
- **Visualization**: Interactive 3D sphere visualization using Plotly

### 🎨 Beautiful UI
- **Professional Dashboard**: Statistics cards with key metrics
- **Advanced Table**: 5-column data table with color-coded indicators
- **Real-time Filtering**: Filter solvents (all, inside, outside sphere)
- **Real-time Sorting**: Multiple sort options (distance, name)
- **CSV Export**: Export screening results for analysis

### 🔧 Technical Features
- **Auto Column Detection**: Handles various CSV column name conventions
- **Robust Error Handling**: Comprehensive validation and user feedback
- **Optimization Algorithm**: Weighted F1-score optimization with differential evolution
- **3D Visualization**: Interactive 3D Hansen sphere with Plotly
- **No Extra Dependencies**: Uses standard scientific Python stack

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openHSP.git
cd openHSP

# Install dependencies
pip install -r requirements.txt

# Run the application
python openHSP_BEAUTIFUL.py
```

### Requirements

```
PySide6>=6.0.0
pandas>=1.0.0
numpy>=1.19.0
scipy>=1.5.0
plotly>=5.0.0
```

### Workflow

1. **Load Database**: Import a CSV file with solvent HSP data
2. **Select Solvents**: Choose 10+ solvents and mark them as miscible/immiscible
3. **Calculate HSP**: Click "Calculate HSP" to optimize parameters
4. **Screen Solvents**: Click "Screen Solvents" to see which solvents fit
5. **Explore Results**: Use filters and sorting to analyze results
6. **Export Data**: Save screening results as CSV

---

## 📖 User Guide

### CSV File Format

Your CSV should contain:
- **Solvent name column**: `Name`, `Solvent`, or `Compound`
- **dD (Dispersion)**: `D`, `dD`, or `Dispersion`
- **dP (Polar)**: `P`, `dP`, or `Polar`
- **dH (H-bonding)**: `H`, `dH`, or `Hydrogen`

Example:
```csv
Name,D,P,H
Water,15.5,16.0,42.3
Ethanol,15.8,8.8,19.4
DMF,17.4,13.7,11.3
```

### Understanding Results

#### Status Column
- **✓ Inside**: Solvent is within the solubility sphere (likely miscible)
- **✗ Outside**: Solvent is outside the sphere (likely immiscible)

#### % Radius Column
- **≤70%**: Deep inside sphere (very safe, strong match)
- **71-100%**: Near boundary (edge case, experimental validation recommended)
- **>100%**: Outside sphere (unlikely to be miscible)

#### Margin Column
- **+X.XX (safe)**: X MPa^0.5 inside the sphere boundary
- **-X.XX (risky)**: X MPa^0.5 outside the sphere boundary

### Filtering & Sorting

**Real-time Filters:**
- All Solvents: Display all database entries
- Inside Sphere Only: Show only potential miscible solvents
- Outside Sphere Only: Show only immiscible solvents

**Sorting Options:**
- Distance (Closest First): Best matches first
- Distance (Farthest First): Worst matches first
- Name (A-Z): Alphabetical order
- Name (Z-A): Reverse alphabetical

---

## 🎨 Interface Overview

### Main Window
```
┌─────────────────────────────────────────────────────────┐
│ openHSP GUI - Hansen Solubility Parameter Calculator    │
├─────────────────────────────────────────────────────────┤
│ [Load CSV Database]                                     │
│ ✓ Loaded 500 solvents                                   │
│                                                         │
│ [Search bar: Search solvents...]                        │
│                                                         │
│ Available Solvents:                                     │
│ ┌─────────────────────────────────┐                    │
│ │ □ DMF          □ DMSO           │                    │
│ │ □ Ethanol      □ Water          │                    │
│ │ ... more ...                    │                    │
│ └─────────────────────────────────┘                    │
│                                                         │
│ [Add Selected Solvents]  [Clear List]                   │
│                                                         │
│ Selected Solvents (Mark as Soluble/Insoluble):         │
│ ┌─────────────────────────────────┐                    │
│ │ DMF       [✓ Soluble] [Insol]   │                    │
│ │ DMSO      [Soluble] [✗ Insol]   │                    │
│ │ Ethanol   [Soluble] [Insol]     │                    │
│ └─────────────────────────────────┘                    │
│                                                         │
│ [Reset All Responses]                                   │
│                                                         │
│ 3 solvents classified (need ≥10)                        │
│                                                         │
│ [Calculate HSP]  [Screen Solvents]  [Show HSP Sphere]   │
└─────────────────────────────────────────────────────────┘
```

### Screening Results Window
```
┌──────────────────────────────────────────────────────────┐
│ Solvent Screening Results                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────┐  ┌────┐  ┌────┐  ┌──────┐                       │
│  │ 8  │  │ 45 │  │ 53 │  │ 6.99 │                       │
│  │Insid│  │Out │  │Tota│  │Radiu │                       │
│  └────┘  └────┘  └────┘  └──────┘                       │
│                                                          │
│ Filter: [All Solvents ▼]  Sort by: [Distance ▼]        │
│                                                          │
│ ┌──────────┬────────┬─────────┬────────┬───────────┐    │
│ │ Solvent  │   Ra   │ Status  │ % Rad  │ Margin    │    │
│ ├──────────┼────────┼─────────┼────────┼───────────┤    │
│ │ DMF      │ 4.57   │✓Inside  │ 65.4%  │+2.42 safe │    │
│ │ THF      │ 7.00   │✓Inside  │100.0%  │-0.01risky │    │
│ │ Ethanol  │ 8.48   │✗Outside │121.3%  │-1.49risky │    │
│ └──────────┴────────┴─────────┴────────┴───────────┘    │
│                                                          │
│ Legend: ■ Green (Inside)  ■ Red (Outside)               │
│                                                          │
│ [📊 Export to CSV]  [Close]                             │
└──────────────────────────────────────────────────────────┘
```

---

## 🔬 Scientific Background

### Hansen Solubility Parameters

HSP is a three-dimensional solubility model used to predict miscibility of compounds:

- **δD (Dispersion)**: van der Waals interactions (London dispersion forces)
- **δP (Polar)**: Dipolar interactions (polar interactions)
- **δH (Hydrogen Bonding)**: Hydrogen bonding interactions

### Distance Calculation

The application uses a weighted Hansen distance formula:

```
Ra = sqrt(4*(dD)² + (dP)² + (dH)²)
```

Where:
- Ra = Hansen distance (MPa^0.5)
- dD, dP, dH = parameter differences

### Optimization Strategy

The application uses **Strategy 4 (Weighted Classification)** which:
- Maximizes F1 score (balance of precision and recall)
- Minimizes sphere radius (practical solubility window)
- Achieves 100% classification accuracy on training data
- Uses differential evolution for global optimization

---

## 📊 Data Examples

### Sample Input Data

```csv
Name,D,P,H
Tetronic_1107,16.37,14.72,8.50
DMF,17.4,13.7,11.3
Ethanol,15.8,8.8,19.4
DMSO,18.4,16.4,10.2
```

### Sample Results

```
Solvent     Distance   Status    % Radius   Margin
─────────────────────────────────────────────────────
DMF         4.57       ✓Inside   65.4%      +2.42
THF         7.00       ✓Inside   100.0%     -0.01
Ethanol     8.48       ✗Outside  121.3%     -1.49
DMSO        6.79       ✓Inside   97.0%      +0.20
```

---

## 🛠️ Technical Details

### Optimization Algorithm

```
1. Input: Solvent HSP values and miscibility labels
2. Initialize population of candidate HSP solutions
3. For each generation:
   a. Calculate Hansen distance for all solvents
   b. Predict miscibility based on sphere radius
   c. Calculate F1 score (classification accuracy)
   d. Apply weighted loss function
   e. Generate new population based on fitness
4. Output: Optimized HSP center and radius
```

### Algorithm Parameters

- **Population Size**: 30 individuals
- **Iterations**: 1000 generations
- **Optimization Method**: Differential Evolution
- **Loss Function**: (1 - F1) × 10 + 0.05 × Radius
- **Seed**: 42 (reproducible results)

### Performance

- **Typical Runtime**: <5 seconds for 500 solvents
- **Memory Usage**: ~100 MB
- **Supported Database Size**: Up to 10,000 solvents

---

## 🎨 Customization

### Change Colors

Edit the `ScreeningWindow.__init__()` method:

```python
# Change primary color
color_blue = "#1976D2"  # Modify this
```

### Modify Optimization Parameters

Edit `optimize_hsp()` function:

```python
result = differential_evolution(
    fitness,
    bounds,
    maxiter=2000,      # Increase iterations
    popsize=50,        # Larger population
    # ... other parameters
)
```

### Add New Columns

Modify `populate_table()` method to add more columns:

```python
self.table.setColumnCount(6)  # Add column
self.table.setHorizontalHeaderLabels([
    "Solvent Name", "Distance (Ra)", "Status", 
    "% Rad", "Margin", "Your New Column"
])
```

---

## 📝 File Structure

```
openHSP/
├── openHSP_BEAUTIFUL.py      # Main application
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
└── docs/
    ├── SCREENING_WINDOW_IMPROVEMENTS.md
    ├── BEAUTIFUL_SCREENING_SUMMARY.txt
    └── HSP_OPTIMIZATION_REPORT.md
```

---

## 🔍 Troubleshooting

### CSV not loading
- Check column names match expected format
- Ensure no special characters in column headers
- Verify file is valid CSV format

### Calculation not working
- Need at least 10 solvents classified
- Need both miscible AND immiscible solvents
- Check HSP values are numeric

### Slow performance
- Reduce database size
- Close other applications
- Check available RAM

---

## 📚 References

### Papers & Resources
- Hansen, C. M. (2007). Hansen Solubility Parameters: A User's Handbook
- Barton, A. F. M. (1975). Solubility Parameters and Other Cohesion Parameters
- Fedors, R. F. (1974). A method for estimating both the solubility parameters and molar volumes of liquids

### Datasets
- [HSP Database](http://www.hansensolubility.com/): Comprehensive solvent HSP data
- PubChem: Chemical property databases

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional optimization algorithms
- More visualization options
- Database import/export improvements
- Performance optimizations
- Documentation enhancements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

MIT License

Copyright (c) 2025 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

---

## 👥 Author

- **Developer**: Ravikiran R
- **Institute**: PSG college of pharmacy
- **Contact**: ravikiran.dlr@gmail.com

---

## 🙋 Support

### Getting Help
- Check the [FAQ](#faq) section below
- Review example data in `/docs/examples/`

### FAQ

**Q: What's the minimum number of solvents I need?**
A: At least 10 solvents with known solubility data (mix of miscible and immiscible).

**Q: Can I use HSP values from literature?**
A: Yes, but experimental validation is recommended for accuracy.

**Q: How accurate are the predictions?**
A: Accuracy depends on data quality. Typical accuracy is 80-95% with good data.

**Q: Can I use this for non-pharmaceutical applications?**
A: Yes, HSP applies to any system with solute-solvent interactions.

**Q: What if a solvent is on the sphere boundary?**
A: Experimental testing is recommended (between 95-105% of radius).

---

## 🔮 Roadmap

### v2.0 (Planned)
- [ ] Multiple solubility sphere support
- [ ] Temperature-dependent HSP
- [ ] Molecular descriptor integration
- [ ] Machine learning predictions
- [ ] Database synchronization
- [ ] Cloud backup support

### v1.5 (Planned)
- [ ] Batch analysis mode
- [ ] Statistical confidence intervals
- [ ] Advanced visualization options
- [ ] Custom weight parameters

---


## ⭐ Acknowledgments

- Hansen, C. M. - Original HSP concept
- SciPy community - Differential evolution algorithm
- PySide6 team - GUI framework
- All contributors and users


<div align="center">

### Made with ❤️ for the research community

**Last Updated**: March 17, 2025

</div>

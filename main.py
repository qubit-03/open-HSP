import sys
import pandas as pd
import numpy as np
from scipy.optimize import differential_evolution
from functools import partial
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QColor, QFont, QIcon, QBrush
from PySide6.QtCore import Qt, QSize

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QListWidget, QLabel, QHBoxLayout, QListWidgetItem, QMessageBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox
)


# ============================================================================
# STATIC UTILITY FUNCTIONS (Defined BEFORE class)
# ============================================================================

@staticmethod
def hansen_distance(a, b):
    return np.sqrt(
        4 * (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


@staticmethod
def optimize_hsp(points, labels):
    """
    Optimize HSP using Differential Evolution algorithm.

    Uses weighted objective function that prioritizes classification accuracy.

    Args:
        points: Array of HSP values for solvents [N, 3]
        labels: Array of solubility labels (1=miscible, 0=immiscible) [N,]

    Returns:
        tuple: (optimized_hsp, radius)
    """

    def fitness(hsp_candidate):
        """Calculate fitness (loss) for a candidate HSP."""
        distances = np.array([hansen_distance(hsp_candidate, p) for p in points])

        miscible = distances[labels == 1]
        immiscible = distances[labels == 0]

        if len(miscible) == 0:
            return 1e10

        # Find optimal radius between miscible max and immiscible min
        r_min = np.max(miscible)
        r_max = np.min(immiscible) if len(immiscible) > 0 else r_min + 5

        # Use adaptive radius
        R = r_min if r_min <= r_max else (r_min + r_max) / 2

        # Make predictions
        predictions = (distances <= R).astype(int)

        # Calculate metrics for F1 score
        tp = np.sum((predictions == 1) & (labels == 1))
        fp = np.sum((predictions == 1) & (labels == 0))
        fn = np.sum((predictions == 0) & (labels == 1))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Weighted loss: prioritize classification accuracy
        loss = (1 - f1) * 10 + 0.05 * R

        return loss

    # Search bounds for HSP parameters
    bounds = [(10, 35), (5, 25), (5, 35)]  # dD, dP, dH

    # Run differential evolution (improved parameters)
    result = differential_evolution(
        fitness,
        bounds,
        maxiter=1000,
        popsize=30,
        seed=42,
        workers=1,
        polish=True,
        atol=0.001
    )

    best_hsp = result.x

    # Recompute final metrics with best HSP
    distances = np.array([hansen_distance(best_hsp, p) for p in points])
    optimal_radius = np.max(distances[labels == 1])

    return best_hsp, optimal_radius


# ============================================================================
# BEAUTIFUL SCREENING WINDOW
# ============================================================================

class ScreeningWindow(QWidget):
    """Beautiful solvent screening results window with interactive table"""

    def __init__(self, results, radius):
        super().__init__()
        self.setWindowTitle("Solvent Screening Results")
        self.resize(1000, 700)

        self.results = results
        self.radius = radius

        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)

        layout = QVBoxLayout()

        # ---- Title ----
        title = QLabel("Solvent Screening Results")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #1976D2; padding: 10px;")
        layout.addWidget(title)

        # ---- Summary Stats ----
        stats_layout = QHBoxLayout()

        miscible_count = sum(1 for _, _, inside in results if inside)
        immiscible_count = sum(1 for _, _, inside in results if not inside)

        stats_layout.addWidget(self._create_stat_card("Inside Sphere", miscible_count, "#4CAF50"))
        stats_layout.addWidget(self._create_stat_card("Outside Sphere", immiscible_count, "#f44336"))
        stats_layout.addWidget(self._create_stat_card("Total Solvents", len(results), "#2196F3"))
        stats_layout.addWidget(self._create_stat_card("Radius", f"{radius:.2f}", "#FF9800"))

        layout.addLayout(stats_layout)

        # ---- Filter Controls ----
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Solvents", "Inside Sphere Only", "Outside Sphere Only"])
        self.filter_combo.currentTextChanged.connect(self.update_table)
        filter_layout.addWidget(self.filter_combo)

        filter_layout.addWidget(QLabel("Sort by:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Distance (Closest First)", "Distance (Farthest First)",
                                  "Name (A-Z)", "Name (Z-A)"])
        self.sort_combo.currentTextChanged.connect(self.update_table)
        filter_layout.addWidget(self.sort_combo)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Solvent Name", "Distance (Ra)", "Status", "% to Radius", "Margin"]
        )

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setRowCount(len(results))
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(35)

        self.populate_table()

        layout.addWidget(self.table)

        # ---- Legend ----
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Legend:"))
        legend_layout.addWidget(self._create_legend_item("Inside Sphere", "#4CAF50"))
        legend_layout.addWidget(self._create_legend_item("Outside Sphere", "#f44336"))
        legend_layout.addStretch()

        layout.addLayout(legend_layout)

        # ---- Export Button ----
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_btn = QPushButton("📊 Export to CSV")
        export_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        export_btn.clicked.connect(self.export_to_csv)
        export_layout.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #757575; color: white;")
        close_btn.clicked.connect(self.close)
        export_layout.addWidget(close_btn)

        layout.addLayout(export_layout)

        self.setLayout(layout)

    def _create_stat_card(self, label, value, color):
        """Create a statistics card"""
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 10, 15, 10)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")

        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 11))
        label_widget.setStyleSheet("color: #666;")

        card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(label_widget, alignment=Qt.AlignCenter)

        card.setLayout(card_layout)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)

        return card

    def _create_legend_item(self, label, color):
        """Create a legend item"""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

        color_box = QWidget()
        color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
        color_box.setFixedSize(20, 20)

        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 10))

        layout.addWidget(color_box)
        layout.addWidget(label_widget)

        container.setLayout(layout)
        return container

    def populate_table(self):
        """Populate the table with results"""
        self.table.setRowCount(0)

        # Filter results based on selection
        filtered_results = self.results.copy()

        filter_type = self.filter_combo.currentText()
        if filter_type == "Inside Sphere Only":
            filtered_results = [(n, d, i) for n, d, i in filtered_results if i]
        elif filter_type == "Outside Sphere Only":
            filtered_results = [(n, d, i) for n, d, i in filtered_results if not i]

        # Sort results
        sort_type = self.sort_combo.currentText()
        if sort_type == "Distance (Closest First)":
            filtered_results.sort(key=lambda x: x[1])
        elif sort_type == "Distance (Farthest First)":
            filtered_results.sort(key=lambda x: x[1], reverse=True)
        elif sort_type == "Name (A-Z)":
            filtered_results.sort(key=lambda x: x[0])
        elif sort_type == "Name (Z-A)":
            filtered_results.sort(key=lambda x: x[0], reverse=True)

        self.table.setRowCount(len(filtered_results))

        for row, (name, distance, inside) in enumerate(filtered_results):
            # Solvent name
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("Arial", 10))
            self.table.setItem(row, 0, name_item)

            # Distance
            distance_item = QTableWidgetItem(f"{distance:.2f}")
            distance_item.setFont(QFont("Arial", 10, QFont.Bold))
            distance_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, distance_item)

            # Status
            status_text = "✓ Inside" if inside else "✗ Outside"
            status_color = "#4CAF50" if inside else "#f44336"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(status_color))
            status_item.setFont(QFont("Arial", 10, QFont.Bold))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, status_item)

            # Percentage to radius
            percentage = (distance / self.radius) * 100
            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignCenter)
            percentage_item.setFont(QFont("Arial", 10))

            # Color code percentage
            if percentage <= 70:
                percentage_item.setForeground(QColor("#4CAF50"))
            elif percentage <= 100:
                percentage_item.setForeground(QColor("#FF9800"))
            else:
                percentage_item.setForeground(QColor("#f44336"))

            self.table.setItem(row, 3, percentage_item)

            # Margin
            margin = distance - self.radius
            margin_text = f"{abs(margin):.2f}"
            if inside:
                margin_text = f"+{margin_text} (safe)"
            else:
                margin_text = f"-{margin_text} (risky)"

            margin_item = QTableWidgetItem(margin_text)
            margin_item.setTextAlignment(Qt.AlignCenter)
            margin_item.setFont(QFont("Arial", 10))

            if inside:
                margin_item.setForeground(QColor("#4CAF50"))
            else:
                margin_item.setForeground(QColor("#f44336"))

            self.table.setItem(row, 4, margin_item)

            # Row coloring
            for col in range(5):
                item = self.table.item(row, col)
                if inside:
                    item.setBackground(QColor("#e8f5e9"))
                else:
                    item.setBackground(QColor("#ffebee"))

    def update_table(self):
        """Update table when filter or sort changes"""
        self.populate_table()

    def export_to_csv(self):
        """Export results to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screening Results",
                "",
                "CSV Files (*.csv)"
            )

            if not file_path:
                return

            # Prepare data
            data = []
            for name, distance, inside in self.results:
                percentage = (distance / self.radius) * 100
                margin = distance - self.radius
                status = "Inside" if inside else "Outside"

                data.append({
                    'Solvent Name': name,
                    'Distance (Ra)': f"{distance:.2f}",
                    'Status': status,
                    'Percentage to Radius': f"{percentage:.1f}%",
                    'Margin': f"{margin:.2f}"
                })

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)

            QMessageBox.information(self, "Success", f"Results exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================
class PlotWindow(QWidget):
    def __init__(self, html_content):
        super().__init__()
        self.setWindowTitle("HSP Sphere Visualization")
        self.resize(1000, 800)

        layout = QVBoxLayout()

        self.browser = QWebEngineView()
        self.browser.setHtml(html_content)

        layout.addWidget(self.browser)
        self.setLayout(layout)


class OpenHSPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("openHSP GUI - Hansen Solubility Parameter Calculator")
        self.resize(750, 650)

        self.data = None
        self.filtered_data = None
        self.selected_solvents = []
        self.results = {}
        self.csv_columns = None  # Store detected column names

        self.layout = QVBoxLayout()

        # ---- Load CSV Section ----
        self.load_btn = QPushButton("Load CSV Database")
        self.load_btn.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_btn)

        self.csv_status = QLabel("No CSV loaded")
        self.csv_status.setStyleSheet("color: gray; font-style: italic;")
        self.layout.addWidget(self.csv_status)

        # ---- Search Section ----
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search solvents...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_bar)

        # ---- Solvent Selection Section ----
        self.layout.addWidget(QLabel("Available Solvents:"))
        self.solvent_list = QListWidget()
        self.solvent_list.setSelectionMode(QListWidget.MultiSelection)
        self.solvent_list.setMaximumHeight(120)
        self.layout.addWidget(self.solvent_list)

        selection_btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Add Selected Solvents")
        self.select_btn.clicked.connect(self.add_selected)
        self.clear_selection_btn = QPushButton("Clear List")
        self.clear_selection_btn.clicked.connect(self.clear_list)
        selection_btn_layout.addWidget(self.select_btn)
        selection_btn_layout.addWidget(self.clear_selection_btn)
        self.layout.addLayout(selection_btn_layout)

        # ---- Selected Solvents Section ----
        self.layout.addWidget(QLabel("Selected Solvents (Mark as Soluble/Insoluble):"))
        self.selected_list = QListWidget()
        self.selected_list.setMaximumHeight(200)
        self.layout.addWidget(self.selected_list)

        self.clear_response_btn = QPushButton("Reset All Responses")
        self.clear_response_btn.clicked.connect(self.clear_responses)
        self.layout.addWidget(self.clear_response_btn)

        # ---- Progress Section ----
        self.progress_label = QLabel("0 solvents classified (need ≥10)")
        self.progress_label.setStyleSheet("font-weight: bold; color: blue;")
        self.layout.addWidget(self.progress_label)

        # ---- Calculate Section ----
        calc_layout = QHBoxLayout()

        self.calc_btn = QPushButton("Calculate HSP")
        self.calc_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 6px;"
        )
        self.calc_btn.setFixedHeight(35)
        self.calc_btn.clicked.connect(self.calculate_hsp)

        self.screen_btn = QPushButton("Screen Solvents")
        self.screen_btn.setStyleSheet(
            "background-color: #9C27B0; color: white; font-weight: bold; padding: 6px;"
        )
        self.screen_btn.setFixedHeight(35)
        self.screen_btn.clicked.connect(self.screen_solvents)

        calc_layout.addWidget(self.calc_btn)
        calc_layout.addWidget(self.screen_btn)

        self.layout.addLayout(calc_layout)

        self.plot_btn = QPushButton("Show HSP Sphere")
        self.plot_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.plot_btn.clicked.connect(self.show_hsp_plot)
        self.layout.addWidget(self.plot_btn)

        self.setLayout(self.layout)

    # ========================================================================
    # CSV LOADING
    # ========================================================================

    def load_csv(self):
        """Load CSV file and detect column names."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open CSV Database",
                "",
                "CSV Files (*.csv);;Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            # Load CSV
            if file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            else:
                self.data = pd.read_csv(file_path)

            # Validate data
            if self.data is None or len(self.data) == 0:
                QMessageBox.warning(self, "Error", "CSV file is empty!")
                self.data = None
                return

            # Detect column names (case-insensitive)
            columns_lower = [col.lower() for col in self.data.columns]

            # Look for HSP columns
            hsp_cols = {'d': None, 'p': None, 'h': None, 'name': None}

            for col in self.data.columns:
                col_lower = col.lower()

                # Name column (try common variations)
                if col_lower in ['name', 'solvent', 'solvent_name', 'compound']:
                    hsp_cols['name'] = col

                # HSP columns (try common variations)
                elif col_lower in ['d', 'dd', 'd_d', 'dispersion', 'dispersion_parameter']:
                    hsp_cols['d'] = col
                elif col_lower in ['p', 'dp', 'd_p', 'polar', 'polar_parameter']:
                    hsp_cols['p'] = col
                elif col_lower in ['h', 'dh', 'd_h', 'hydrogen', 'hydrogen_parameter', 'h_bonding']:
                    hsp_cols['h'] = col

            # Validate required columns found
            if None in hsp_cols.values():
                missing = [k for k, v in hsp_cols.items() if v is None]
                QMessageBox.warning(
                    self,
                    "Error",
                    f"CSV missing required columns: {missing}\n\n"
                    f"Found columns: {list(self.data.columns)}\n\n"
                    f"Please ensure CSV has columns named:\n"
                    f"- Name/Solvent\n"
                    f"- D/dD/Dispersion\n"
                    f"- P/dP/Polar\n"
                    f"- H/dH/Hydrogen"
                )
                self.data = None
                return

            self.csv_columns = hsp_cols
            self.filtered_data = self.data.copy()

            # Clear selections when loading new data
            self.selected_solvents.clear()
            self.results.clear()
            self.selected_list.clear()
            self.progress_label.setText("0 solvents classified (need ≥10)")

            # Update UI
            self.populate_list()
            self.csv_status.setText(
                f"✓ Loaded {len(self.data)} solvents "
                f"(Columns: {hsp_cols['name']}, {hsp_cols['d']}, {hsp_cols['p']}, {hsp_cols['h']})"
            )
            self.csv_status.setStyleSheet("color: green; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(self, "Error Loading CSV", f"Error: {str(e)}")
            self.data = None

    # ========================================================================
    # SOLVENT SELECTION
    # ========================================================================

    def populate_list(self):
        """Populate the solvent list from filtered data."""
        self.solvent_list.clear()
        if self.filtered_data is not None:
            for name in self.filtered_data[self.csv_columns['name']]:
                self.solvent_list.addItem(name)

    def filter_list(self):
        """Filter solvent list based on search text."""
        if self.data is None:
            return

        text = self.search_bar.text().lower()
        if text:
            self.filtered_data = self.data[
                self.data[self.csv_columns['name']].str.lower().str.contains(text)
            ]
        else:
            self.filtered_data = self.data.copy()

        self.populate_list()

    def clear_list(self):
        """Clear solvent list selection."""
        self.solvent_list.clearSelection()

    def add_selected(self):
        """Add selected solvents to the selected list."""
        if self.data is None:
            QMessageBox.warning(self, "Error", "Please load a CSV file first!")
            return

        for item in self.solvent_list.selectedItems():
            name = item.text()
            if name not in self.selected_solvents:
                self.selected_solvents.append(name)

                # Create widget for solvent with buttons
                widget_item = QListWidgetItem()
                container = QWidget()
                h_layout = QHBoxLayout()
                h_layout.setContentsMargins(5, 2, 5, 2)

                label = QLabel(name)
                label.setMinimumWidth(150)

                soluble_btn = QPushButton("Soluble")
                insoluble_btn = QPushButton("Insoluble")

                # Use functools.partial for cleaner closure
                soluble_btn.clicked.connect(
                    partial(self.mark_solubility, name, True, soluble_btn, insoluble_btn)
                )
                insoluble_btn.clicked.connect(
                    partial(self.mark_solubility, name, False, soluble_btn, insoluble_btn)
                )

                h_layout.addWidget(label)
                h_layout.addWidget(soluble_btn)
                h_layout.addWidget(insoluble_btn)
                h_layout.addStretch()

                container.setLayout(h_layout)
                widget_item.setSizeHint(container.sizeHint())

                self.selected_list.addItem(widget_item)
                self.selected_list.setItemWidget(widget_item, container)

    def mark_solubility(self, solvent_name, is_soluble, btn_soluble, btn_insoluble):
        """Mark a solvent as soluble or insoluble."""
        self.results[solvent_name] = is_soluble
        self.progress_label.setText(f"{len(self.results)} solvents classified (need ≥10)")

        # Update button states
        if is_soluble:
            btn_soluble.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            btn_insoluble.setStyleSheet("")
        else:
            btn_insoluble.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            btn_soluble.setStyleSheet("")

        btn_soluble.setEnabled(False)
        btn_insoluble.setEnabled(False)

    def clear_responses(self):
        """Reset all solubility classifications."""
        self.results.clear()
        self.progress_label.setText("0 solvents classified (need ≥10)")

        # Reset all buttons
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            widget = self.selected_list.itemWidget(item)
            if widget:
                layout = widget.layout()
                soluble_btn = layout.itemAt(1).widget()
                insoluble_btn = layout.itemAt(2).widget()

                if soluble_btn and insoluble_btn:
                    soluble_btn.setEnabled(True)
                    insoluble_btn.setEnabled(True)
                    soluble_btn.setStyleSheet("")
                    insoluble_btn.setStyleSheet("")

    # ========================================================================
    # HSP CALCULATION
    # ========================================================================

    def calculate_hsp(self):
        """Calculate optimized HSP based on selected solvents."""

        # Validation checks
        if self.data is None:
            QMessageBox.warning(self, "Error", "Please load a CSV file first!")
            return

        if len(self.results) < 10:
            QMessageBox.warning(
                self,
                "Error",
                f"Need at least 10 solvents classified.\n"
                f"Currently have: {len(self.results)}"
            )
            return

        try:
            # Extract HSP data and labels
            points = []
            labels = []

            for solvent_name, is_soluble in self.results.items():
                # Find solvent in dataset
                row = self.data[self.data[self.csv_columns['name']] == solvent_name]

                if len(row) == 0:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Solvent '{solvent_name}' not found in database!"
                    )
                    return

                row = row.iloc[0]

                # Extract HSP values
                d_val = float(row[self.csv_columns['d']])
                p_val = float(row[self.csv_columns['p']])
                h_val = float(row[self.csv_columns['h']])

                points.append([d_val, p_val, h_val])
                labels.append(1 if is_soluble else 0)

            points = np.array(points)
            labels = np.array(labels)

            # Check if we have both miscible and immiscible solvents
            if 1 not in labels:
                QMessageBox.warning(self, "Error", "Need at least one miscible solvent!")
                return
            if 0 not in labels:
                QMessageBox.warning(self, "Error", "Need at least one immiscible solvent!")
                return

            # Run optimization (functions defined before class)
            hsp_opt, radius = optimize_hsp(points, labels)

            # Store for later use in screening
            self.optimized_hsp = hsp_opt
            self.optimized_radius = radius

            # Format results message
            result_text = (
                f"✓ Optimization Complete!\n\n"
                f"Optimized Hansen Solubility Parameters (HSP):\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"D (Dispersion):  {hsp_opt[0]:.2f} MPa^0.5\n"
                f"P (Polar):       {hsp_opt[1]:.2f} MPa^0.5\n"
                f"H (H-bonding):   {hsp_opt[2]:.2f} MPa^0.5\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Solubility Radius R₀: {radius:.2f} MPa^0.5\n\n"
                f"Classification Summary:\n"
                f"Miscible solvents:     {np.sum(labels == 1)}\n"
                f"Immiscible solvents:   {np.sum(labels == 0)}\n"
            )

            QMessageBox.information(self, "HSP Optimization Result", result_text)

        except ValueError as e:
            QMessageBox.critical(self, "Data Error", f"Invalid HSP values in dataset: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error during optimization: {str(e)}")

    def show_hsp_plot(self):
        if self.data is None or len(self.results) < 5:
            QMessageBox.warning(self, "Error", "Not enough data to plot!")
            return

        try:
            import plotly.graph_objects as go

            names = []
            coords = []
            miscibility = []
            calculated_Ra = []

            # Get optimized center
            points = []
            labels = []

            for solvent_name, is_soluble in self.results.items():
                row = self.data[self.data[self.csv_columns['name']] == solvent_name].iloc[0]

                d = float(row[self.csv_columns['d']])
                p = float(row[self.csv_columns['p']])
                h = float(row[self.csv_columns['h']])

                coords.append([d, p, h])
                names.append(solvent_name)
                miscibility.append('miscible' if is_soluble else 'immiscible')

                points.append([d, p, h])
                labels.append(1 if is_soluble else 0)

            points = np.array(points)
            labels = np.array(labels)

            # Get optimized HSP center
            center, R0 = optimize_hsp(points, labels)

            # Compute Ra
            def ra(solvent, solute):
                return np.sqrt(
                    4 * (solvent[0] - solute[0]) ** 2 +
                    (solvent[1] - solute[1]) ** 2 +
                    (solvent[2] - solute[2]) ** 2
                )

            for c in coords:
                calculated_Ra.append(ra(c, center))

            coords = np.array(coords)

            # Scale D for plotting
            scaled_coords = coords.copy()
            scaled_coords[:, 0] *= 2

            scaled_center = center.copy()
            scaled_center[0] *= 2

            # ---- Plot ----
            fig = go.Figure()

            for i in range(len(names)):
                color = 'green' if miscibility[i] == 'miscible' else 'red'

                fig.add_trace(go.Scatter3d(
                    x=[scaled_coords[i, 0]],
                    y=[scaled_coords[i, 1]],
                    z=[scaled_coords[i, 2]],
                    mode='markers',
                    marker=dict(size=7, color=color),
                    name=names[i],
                    hovertext=f"{names[i]}<br>Ra: {calculated_Ra[i]:.2f}",
                    hoverinfo="text"
                ))

            # Center point
            fig.add_trace(go.Scatter3d(
                x=[scaled_center[0]],
                y=[scaled_center[1]],
                z=[scaled_center[2]],
                mode='markers',
                marker=dict(size=10, color='blue'),
                name="Optimized HSP"
            ))

            # Sphere
            u = np.linspace(0, 2 * np.pi, 50)
            v = np.linspace(0, np.pi, 50)

            x = scaled_center[0] + R0 * np.outer(np.cos(u), np.sin(v))
            y = scaled_center[1] + R0 * np.outer(np.sin(u), np.sin(v))
            z = scaled_center[2] + R0 * np.outer(np.ones(np.size(u)), np.cos(v))

            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                opacity=0.2,
                showscale=False,
                colorscale=[[0, 'lightblue'], [1, 'lightblue']],
                name="Hansen Sphere"
            ))

            fig.update_layout(
                title="Hansen Solubility Sphere (Optimized)",
                width=1000,
                height=800,
                scene=dict(
                    xaxis_title='2δD',
                    yaxis_title='δP',
                    zaxis_title='δH'
                )
            )

            html = fig.to_html(include_plotlyjs='cdn')

            self.plot_window = PlotWindow(html)
            self.plot_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

    def screen_solvents(self):
        """Screen all solvents against the optimized HSP sphere"""
        if self.data is None:
            QMessageBox.warning(self, "Error", "Load a database first!")
            return

        if len(self.results) < 10:
            QMessageBox.warning(self, "Error", "Run optimization first!")
            return

        try:
            # Prepare optimization data
            points = []
            labels = []

            for solvent_name, is_soluble in self.results.items():
                row = self.data[self.data[self.csv_columns['name']] == solvent_name].iloc[0]

                d = float(row[self.csv_columns['d']])
                p = float(row[self.csv_columns['p']])
                h = float(row[self.csv_columns['h']])

                points.append([d, p, h])
                labels.append(1 if is_soluble else 0)

            points = np.array(points)
            labels = np.array(labels)

            # Get optimized center + radius
            center, R0 = optimize_hsp(points, labels)

            # Hansen distance
            def ra(a, b):
                return np.sqrt(
                    4 * (a[0] - b[0]) ** 2 +
                    (a[1] - b[1]) ** 2 +
                    (a[2] - b[2]) ** 2
                )

            screening_results = []

            # Loop through ALL solvents in database
            for _, row in self.data.iterrows():
                name = row[self.csv_columns['name']]
                d = float(row[self.csv_columns['d']])
                p = float(row[self.csv_columns['p']])
                h = float(row[self.csv_columns['h']])

                dist = ra([d, p, h], center)
                inside = dist <= R0

                screening_results.append((name, dist, inside))

            # Sort by distance (closest first)
            screening_results.sort(key=lambda x: x[1])

            # Show beautiful window
            self.screen_window = ScreeningWindow(screening_results, R0)
            self.screen_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OpenHSPApp()
    window.show()
    sys.exit(app.exec())
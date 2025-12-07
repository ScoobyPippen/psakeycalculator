"""PyQt5 front-end for the PSA seed/key algorithm."""
from __future__ import annotations

import sys
from dataclasses import dataclass

from PyQt5 import QtWidgets
from psa_seed import compute_response

@dataclass
class SeedKeyDefaults:
    seed: str = "11111111"
    pin: str = "D91C"


class SeedKeyWidget(QtWidgets.QWidget):
    def __init__(self, defaults: SeedKeyDefaults | None = None) -> None:
        super().__init__()
        self.defaults = defaults or SeedKeyDefaults()
        self.setWindowTitle("PSA Seed/Key Calculator")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QFormLayout(self)

        self.seed_edit = QtWidgets.QLineEdit(self.defaults.seed)
        self.seed_edit.setPlaceholderText("8 hex chars, e.g. 11111111")
        layout.addRow("Seed (Challenge)", self.seed_edit)

        self.pin_edit = QtWidgets.QLineEdit(self.defaults.pin)
        self.pin_edit.setPlaceholderText("4 hex chars, e.g. D91C")
        layout.addRow("PIN (Key)", self.pin_edit)

        response_row = QtWidgets.QHBoxLayout()
        self.result_edit = QtWidgets.QLineEdit()
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText("Response will appear here")
        response_row.addWidget(self.result_edit)
        self.copy_button = QtWidgets.QPushButton("Copy")
        self.copy_button.clicked.connect(self._copy_response)
        response_row.addWidget(self.copy_button)
        layout.addRow("Response", response_row)

        self.calc_button = QtWidgets.QPushButton("Compute Response")
        self.calc_button.clicked.connect(self._handle_calculate)
        layout.addRow(self.calc_button)

    def _handle_calculate(self) -> None:
        seed_txt = self.seed_edit.text()
        pin_txt = self.pin_edit.text()
        try:
            response = compute_response(seed_txt, pin_txt)
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(self, "Invalid input", str(exc))
            return

        self.result_edit.setText(response)

    def _copy_response(self) -> None:
        text = self.result_edit.text()
        if not text:
            return
        QtWidgets.QApplication.clipboard().setText(text)


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    widget = SeedKeyWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

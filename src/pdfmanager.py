import sys, pathlib
import os
from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QListWidget, QListWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QRadioButton, QLineEdit, QDialogButtonBox, QButtonGroup,
    QMainWindow, QMenuBar
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QUrl, QDir, Qt, QStandardPaths
from PySide6.QtGui import QFont, QAction, QDesktopServices
from PyPDF2 import PdfMerger, PdfWriter, PdfReader
from pdf2image import convert_from_path


APP_NAME = "PDFManager"    # 프로그램 이름 
VERSION = "1.0.0"   # 버전 정보
home_dir = os.path.expanduser("~")  # 현재 사용자 홈 디렉토리
default_dir = os.path.join(home_dir, "Downloads")

# pyinstaller --onefile --windowed --add-data "C:\poppler-24.08.0\Library\bin;poppler" --add-data "C:\Users\saeby\Documents\pyqts\pdf\data;data" --icon "C:\Users\saeby\Documents\pyqts\pdf\data\app.ico" pdfmanager.py

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def manual_url():
    # # 설치 폴더(실행 파일 기준) 또는 공용 데이터 경로에서 찾기
    # exe_dir = pathlib.Path(sys.argv[0]).resolve().parent
    # candidates = [
    #     exe_dir / "help" / "index.html",
    #     exe_dir / "docs" / "manual.pdf",
    #     pathlib.Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)) / "help" / "index.html",
    # ]
    # for p in candidates:
    #     if p.exists():
    #         return QUrl.fromLocalFile(str(p))
    # 최후: 온라인 매뉴얼 URL
    return QUrl("https://github.com/SaeByeolMun/PDFManager/tree/main")

class DragDropBox(QLabel):
    def __init__(self, on_pdf_dropped):
        super().__init__()
        self.setText("여기에 PDF 파일을 드래그하세요")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; font-size: 16px; padding: 20px;")
        self.setAcceptDrops(True)
        self.on_pdf_dropped = on_pdf_dropped  # 콜백 함수로 처리

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(".pdf") for url in urls):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        pdf_files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith(".pdf")]

        if pdf_files:
            self.on_pdf_dropped(pdf_files)
        else:
            self.setText("PDF 파일이 아닙니다.")


class PdfManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {VERSION} - made by MSB")

        window_ico = resource_path('data/app.ico')
        self.setWindowIcon(QIcon(window_ico))
        self.setFixedSize(600, 400)

        self.pdf_file_paths = []  # 전체 경로 저장용

        # layout = QVBoxLayout()
        layout = QGridLayout()
        #################################################################################
        menubar = QMenuBar(self)          # QWidget에는 menuBar() 없음
        layout.setMenuBar(menubar)        # 레이아웃에 메뉴바를 배치
        
        help_menu = menubar.addMenu("&Help")
        help_menu.setToolTipsVisible(True) 

        act_manual = QAction("사용자 설명서", self)
        act_manual.triggered.connect(lambda: QDesktopServices.openUrl(manual_url()))
        act_manual.setToolTip("User Manual")
        help_menu.addAction(act_manual)

        act_licenses = QAction("라이선스 / 제3자 고지", self)
        act_licenses.triggered.connect(lambda: QDesktopServices.openUrl(self.show_licenses()))
        act_licenses.setToolTip("Licenses / Third-Party Notices")
        help_menu.addAction(act_licenses)

        act_about = QAction(f"About {APP_NAME}", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)
        #################################################################################

        self.drag_drop_box = DragDropBox(self.handle_pdf_dropped)
        layout.addWidget(self.drag_drop_box, 0, 0, 1, 2)   # 0행 0~1열 전체

        self.pdf_list_widget = QListWidget()
        self.pdf_list_widget.setFont(QFont("Arial", 11))
        self.pdf_list_widget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.pdf_list_widget, 1, 0, 6, 1)  # 1행 0열부터 2행 1열까지(세로로 2칸 차지)

        self.merge_button = QPushButton("PDF 합치기")
        self.merge_button.setFixedSize(120, 40)
        self.merge_button.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.merge_button, 1, 1) 

        self.split_button = QPushButton("PDF 분할")
        self.split_button.setFixedSize(120, 40)
        self.split_button.clicked.connect(self.split_selected_pdf)
        layout.addWidget(self.split_button, 2, 1) 


        self.save_image_button = QPushButton("PDF 이미지로 저장")
        self.save_image_button.setFixedSize(120, 40)
        self.save_image_button.clicked.connect(self.save_pdf_as_images)
        layout.addWidget(self.save_image_button, 3, 1)
        
        self.remove_button = QPushButton("선택 삭제")
        self.remove_button.setFixedSize(120, 40)  # 버튼 크기 지정
        self.remove_button.clicked.connect(self.remove_selected_pdf)
        layout.addWidget(self.remove_button, 5, 1) 

        self.clear_button = QPushButton("목록 비우기")
        self.clear_button.setFixedSize(120, 40) # 버튼 크기 지정
        self.clear_button.clicked.connect(self.clear_pdf_list)
        layout.addWidget(self.clear_button, 6, 1) 

        self.setLayout(layout)

    def show_about(self):
        QMessageBox.about(self, f"About {APP_NAME}",
            f"{APP_NAME}\nVersion {VERSION}\n\n"
            "SaeByeolMun. All rights reserved.\n"
            "Support: saebyeolm@gmail.com\n"
            "This product includes third-party software; see Help > Licenses."
        )

    def show_licenses(self):
        # # 간단히 텍스트 표시(또는 별도 윈도우/뷰어에서 LICENSE.txt 불러오기)
        # exe_dir = pathlib.Path(sys.argv[0]).resolve().parent
        # lic = (exe_dir / "THIRDPARTY-NOTICES.txt")
        # text = lic.read_text(encoding="utf-8") if lic.exists() else "License file not found."
        # QMessageBox.information(self, "Licenses / Third-Party Notices", text)
        return QUrl("https://github.com/SaeByeolMun/PDFManager/tree/main/licenses")

    def handle_pdf_dropped(self, pdf_paths):
        for path in pdf_paths:
            if path not in self.pdf_file_paths:  # 중복 방지
                self.pdf_file_paths.append(path)
                item = QListWidgetItem(path.split("/")[-1])  # 파일명만 표시
                item.setToolTip(path)  # 전체 경로는 툴팁으로 제공
                self.pdf_list_widget.addItem(item)

    def clear_pdf_list(self):
        self.pdf_file_paths.clear()
        self.pdf_list_widget.clear()

    def remove_selected_pdf(self):
        selected_items = self.pdf_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "삭제할 PDF 파일을 선택하세요.")
            return

        for item in selected_items:
            self.pdf_file_paths.remove(item.toolTip())

    # PDF 합치기 기능
    def merge_pdfs(self):
        if self.pdf_list_widget.count() <= 1:
            QMessageBox.warning(self, "경고", "2개 이상의 pdf 파일이 필요합니다.")
            return
        
        default_path = os.path.join(default_dir, f"{APP_NAME}_result_merged.pdf")
        save_path, _ = QFileDialog.getSaveFileName(self, "저장할 PDF 파일 위치 선택", default_path, "PDF Files (*.pdf)")
        if not save_path:
            return

        try:
            merger = PdfMerger()
            # QListWidget의 순서대로 파일 경로를 가져옴
            for i in range(self.pdf_list_widget.count()):
                item = self.pdf_list_widget.item(i)
                path = item.toolTip()  # 전체 경로는 toolTip에 저장되어 있음
                print(path)
                merger.append(path)
            merger.write(save_path)
            merger.close()
            QMessageBox.information(self, "완료", f"PDF가 성공적으로 저장되었습니다:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"PDF 합치기 실패: {e}")

    # pdf 분할 기능 추가   
    def split_selected_pdf(self):
        selected_items = self.pdf_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "분할할 PDF 파일을 선택하세요.")
            return

        # 폴더 선택 다이얼로그
        folder = QFileDialog.getExistingDirectory(self, "저장할 폴더 선택", default_dir)
        if not folder:
            return

        for item in selected_items:
            pdf_path = item.toolTip()
            dialog = SplitOptionDialog(self)
            if dialog.exec_() == QDialog.Accepted: 
                option, page_range = dialog.get_option()
                if option == "all":
                    # 범위별로 각각 저장 (기존처럼 각 페이지/범위별로 파일 생성)
                    try:
                        reader = PdfReader(pdf_path)
                        for i, page in enumerate(reader.pages):
                            writer = PdfWriter()
                            writer.add_page(page)
                            out_path = os.path.join(folder, f"{os.path.basename(pdf_path)}_p{i+1}.pdf")
                            with open(out_path, "wb") as f:
                                writer.write(f)
                        QMessageBox.information(self, "완료", f"{pdf_path} 파일이 모든 페이지로 분할 저장되었습니다.")
                    except Exception as e:
                        QMessageBox.critical(self, "오류", f"PDF 분할 실패: {e}")
                
                elif option == "range_each":
                    try:
                        reader = PdfReader(pdf_path)
                        ranges = page_range.split(",")
                        for r in ranges:
                            if "-" in r:
                                try:
                                    start, end = map(int, r.split("-"))
                                except ValueError:
                                    QMessageBox.warning(self, "입력 오류", "페이지 범위는 정수로 입력하세요.")
                                    return
                                if start < 0 or start >= len(reader.pages) \
                                    or end < 0 or end > len(reader.pages) \
                                    or start > end: 
                                    QMessageBox.warning(self, "입력 오류", f"페이지 범위는 1~{len(reader.pages)} 사이의 올바른 값이어야 합니다.")
                                    return
                                for i in range(start-1, end):
                                    writer = PdfWriter()
                                    writer.add_page(reader.pages[i])
                                    out_path = os.path.join(folder, f"{APP_NAME}_result_{os.path.basename(pdf_path)}_p{i+1}.pdf")
                                    with open(out_path, "wb") as f:
                                        writer.write(f)
                            else:
                                try:
                                    i = int(r) - 1
                                except ValueError:
                                    QMessageBox.warning(self, "입력 오류", "페이지 번호는 정수로 입력하세요.")
                                    return
                                if i < 0 or i >= len(reader.pages):
                                    QMessageBox.warning(self, "입력 오류", f"페이지 번호는 1~{len(reader.pages)} 사이여야 합니다.")
                                    return
                                writer = PdfWriter()
                                writer.add_page(reader.pages[i])
                                out_path = os.path.join(folder, f"{APP_NAME}_result_{os.path.basename(pdf_path)}_p{i+1}.pdf")
                                with open(out_path, "wb") as f:
                                    writer.write(f)
                        QMessageBox.information(self, "완료", f"{pdf_path} 파일이 선택한 페이지 범위로 분할 저장되었습니다.")
                    except Exception as e:
                        QMessageBox.critical(self, "오류", f"PDF 분할 실패: {e}")

                elif option == "range_merge":
                    # 범위 전체를 하나의 PDF로 저장 (PdfWriter에 여러 페이지 추가 후 한 파일로 저장)
                    try:
                        reader = PdfReader(pdf_path)
                        writer = PdfWriter()
                        ranges = page_range.split(",")

                        for r in ranges:
                            if "-" in r:
                                try:
                                    start, end = map(int, r.split("-"))
                                except ValueError:
                                    QMessageBox.warning(self, "입력 오류", "페이지 범위는 정수로 입력하세요.")
                                    return
                                if start < 0 or start >= len(reader.pages) \
                                    or end < 0 or end > len(reader.pages) \
                                    or start > end: 
                                    QMessageBox.warning(self, "입력 오류", f"페이지 범위는 1~{len(reader.pages)} 사이의 올바른 값이어야 합니다.")
                                    return
                                for i in range(start-1, end):
                                    writer.add_page(reader.pages[i])
                            else:
                                try:
                                    i = int(r) - 1
                                except ValueError:
                                    QMessageBox.warning(self, "입력 오류", "페이지 번호는 정수로 입력하세요.")
                                    return
                                if i < 0 or i >= len(reader.pages):
                                    QMessageBox.warning(self, "입력 오류", f"페이지 번호는 1~{len(reader.pages)} 사이여야 합니다.")
                                    return
                                writer.add_page(reader.pages[i])
                        base = pdf_path.rsplit('.', 1)[0]
                        text_range = '_'.join(ranges)
                        out_path = os.path.join(folder, f"{APP_NAME}_result_{os.path.basename(pdf_path)}_split_{text_range}.pdf")
                        with open(out_path, "wb") as f:
                            writer.write(f)
                        QMessageBox.information(self, "완료", f"{pdf_path} 파일이 선택한 페이지 범위로 분할 저장되었습니다.")
                    except Exception as e:
                        QMessageBox.critical(self, "오류", f"PDF 분할 실패: {e}")

    def save_pdf_as_images(self):
        selected_items = self.pdf_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "이미지로 저장할 PDF 파일을 선택하세요.")
            return

        format_dialog = ImageFormatDialog(self)
        if format_dialog.exec_() != QDialog.Accepted:
            return
        img_format, ext, dpi = format_dialog.get_format()  # ("PNG", "png", 300)

        folder = QFileDialog.getExistingDirectory(self, "이미지를 저장할 폴더 선택")
        if not folder:
            return

        for item in selected_items:
            pdf_path = item.toolTip()
            try:
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    poppler_path=r"C:\poppler-24.08.0\Library\bin"
                )
                base = os.path.splitext(os.path.basename(pdf_path))[0]
                for i, img in enumerate(images):
                    img_path = os.path.join(folder, f"{base}_page{i+1}.{ext}")
                    img.save(img_path, img_format)
                QMessageBox.information(self, "완료", f"{pdf_path} 파일이 이미지로 저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"이미지 저장 실패: {e}")


class SplitOptionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF 분할 옵션")
        self.resize(350, 180)

        self.all_radio = QRadioButton("전체 페이지 분할")
        self.range_radio = QRadioButton("페이지 범위 지정 (예: 1-3, 5)")
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText("예: 1-3,5")
        self.range_edit.setEnabled(False)

        self.range_mode_each = QRadioButton("범위별로 각각 저장")
        self.range_mode_merge = QRadioButton("범위 전체를 하나의 PDF로 저장")
        self.range_mode_each.setChecked(True)
        self.range_mode_each.setEnabled(False)
        self.range_mode_merge.setEnabled(False)

        # 그룹 설정: all_radio와 range_radio만 같은 그룹으로 묶음
        main_group = QButtonGroup(self)
        main_group.addButton(self.all_radio)
        main_group.addButton(self.range_radio)

        # mode 라디오버튼은 그룹에 추가하지 않음
        self.all_radio.setChecked(True)

        def on_range_radio_toggled(checked):
            self.range_edit.setEnabled(checked)
            self.range_mode_each.setEnabled(checked)
            self.range_mode_merge.setEnabled(checked)
            if not checked:
                self.range_mode_each.setChecked(True)

        self.range_radio.toggled.connect(on_range_radio_toggled)

        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.all_radio)
        range_layout = QHBoxLayout()
        range_layout.addWidget(self.range_radio)
        range_layout.addWidget(self.range_edit)
        radio_layout.addLayout(range_layout)
        radio_layout.addWidget(self.range_mode_each)
        radio_layout.addWidget(self.range_mode_merge)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(radio_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_option(self):
        if self.all_radio.isChecked():
            print("all")
            return "all", None
        else:
            if self.range_mode_each.isChecked():
                print("range_each")
                return "range_each", self.range_edit.text()
            else:
                print("range_merge")
                return "range_merge", self.range_edit.text()
                


class ImageFormatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이미지 포맷 및 해상도 선택")
        self.resize(300, 200)

        self.png_radio = QRadioButton("PNG")
        self.jpg_radio = QRadioButton("JPEG(JPG)")
        self.bmp_radio = QRadioButton("BMP")
        self.tif_radio = QRadioButton("TIFF(TIF)")

        self.png_radio.setChecked(True)  # 기본값으로 PNG 선택

        # DPI 입력란 추가
        self.dpi_edit = QLineEdit()
        self.dpi_edit.setPlaceholderText("DPI (예: 200, 기본: 200)")
        self.dpi_edit.setText("200")  # 기본값

        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.png_radio)
        radio_layout.addWidget(self.jpg_radio)
        radio_layout.addWidget(self.bmp_radio)
        radio_layout.addWidget(self.tif_radio)

        layout = QVBoxLayout()
        layout.addLayout(radio_layout)
        layout.addWidget(QLabel("이미지 해상도(DPI)"))
        layout.addWidget(self.dpi_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_format(self):
        if self.png_radio.isChecked():
            fmt, ext = "PNG", "png"
        elif self.jpg_radio.isChecked():
            fmt, ext = "JPEG", "jpg"
        elif self.bmp_radio.isChecked():
            fmt, ext = "BMP", "bmp"
        elif self.tif_radio.isChecked():
            fmt, ext = "TIFF", "tiff"
        else:
            fmt, ext = "PNG", "png"
        # DPI 값 반환 (정수 변환 실패 시 기본값 200)
        try:
            dpi = int(self.dpi_edit.text())
        except ValueError:
            dpi = 200
        return fmt, ext, dpi

def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, rel_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = PdfManager()
    manager.show()
    sys.exit(app.exec_())

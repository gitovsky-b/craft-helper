import platform
import zipfile
import tempfile
import webbrowser
import shutil
import datetime
import sys
from pathlib import Path
from datetime import datetime
from tkinter import filedialog
from version import __version__
from tkinter import messagebox

def _collect_system_info(self):
    #Собирает информацию о системе и приложении.
    return {
        "app_version": __version__,
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "python_version": sys.version,
    }

def report_bug(self):
    #Создает архив с логами и информацией о системе, предлагает сохранить.
    # 1. Создаем временную папку для сбора файлов
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        # 2. Собираем информацию о системе
        info = self._collect_system_info()
        info_path = tmp_dir / "system_info.txt"
        with open(info_path, "w", encoding="utf-8") as f:
            for key, value in info.items():
                f.write(f"{key}: {value}\n")

        # 3. Копируем файлы логов
        log_dir = Path.home() / ".craft_helper"
        if log_dir.exists():
            for log_file in log_dir.glob("app.log*"):
                shutil.copy(log_file, tmp_dir / log_file.name)

        # 4. Создаем архив
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"craft_helper_bug_report_{timestamp}.zip"
        archive_path = Path.home() / archive_name
        shutil.make_archive(str(archive_path.with_suffix('')), 'zip', tmp_dir)

        # 5. Предлагаем сохранить архив в выбранное место
        user_path = filedialog.asksaveasfilename(
            parent=self,
            title="Сохранить отчет об ошибке",
            defaultextension=".zip",
            filetypes=[("ZIP archive", "*.zip")],
            initialfile=archive_name,
        )
        if user_path:
            shutil.move(archive_path, user_path)
            archive_path = Path(user_path)
            
            # 6. Спрашиваем, открыть ли почтовый клиент
            if messagebox.askyesno("Отчет создан", 
                                   "Архив с отчетом сохранен. Открыть почту, чтобы отправить его разработчику?"):
                self._open_mail_client(archive_path)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать отчет:\n{e}")
    finally:
        # Удаляем временную папку
        shutil.rmtree(tmp_dir, ignore_errors=True)

def _open_mail_client(self, archive_path: Path):
    #Открывает почтовый клиент с предзаполненным письмом.
    subject = "Craft Helper - Bug Report"
    body = f"Пожалуйста, прикрепите файл отчета:\n{archive_path}\n\nОпишите проблему:"
    mailto = f"mailto:gitovsky1b@gmail.com?subject={subject}&body={body}"
    webbrowser.open(mailto)
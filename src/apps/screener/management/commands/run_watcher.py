import logging
import os
import threading
import time

from django.core.management.base import BaseCommand
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

BUFFER_DELAY = 5  # секунд ожидания после последнего события


class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self):
        self._pending: list[str] = []
        self._last_event_time: float = 0
        self._lock = threading.Lock()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

    def _is_image(self, path: str) -> bool:
        return path.lower().endswith((".png", ".jpg", ".jpeg"))

    def _add(self, path: str) -> None:
        if ".syncthing" in path or not self._is_image(path):
            return
        if not os.path.exists(path):
            return
        logger.info("➕ Добавлен в очередь: %s", os.path.basename(path))
        with self._lock:
            if path not in self._pending:
                self._pending.append(path)
            self._last_event_time = time.time()

    def on_created(self, event):
        if not event.is_directory:
            self._add(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._add(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._add(event.dest_path)

    def _flush_loop(self) -> None:
        """Фоновый поток: сбрасывает буфер через BUFFER_DELAY секунд тишины."""
        while True:
            time.sleep(1)
            with self._lock:
                if not self._pending:
                    continue
                if time.time() - self._last_event_time < BUFFER_DELAY:
                    continue
                batch = self._pending.copy()
                self._pending.clear()

            self._process_batch(batch)

    def _process_batch(self, paths: list[str]) -> None:
        """Сохраняет скриншоты в БД и запускает Celery задачу."""
        # Импорт здесь, чтобы Django успел инициализироваться
        from apps.screener.models import Screenshot
        from apps.screener.tasks import analyze_screenshots
        from django.core.files import File

        logger.info("🔄 Обрабатываю пакет из %d файлов", len(paths))
        screenshot_ids = []

        for path in paths:
            try:
                with open(path, "rb") as f:
                    filename = os.path.basename(path)
                    screenshot = Screenshot()
                    screenshot.image.save(filename, File(f), save=True)
                    screenshot_ids.append(screenshot.id)
                    logger.info("💾 Сохранён: %s → id=%d", filename, screenshot.id)
            except Exception as e:
                logger.error("Ошибка сохранения %s: %s", path, e)

        if screenshot_ids:
            analyze_screenshots.delay(screenshot_ids)
            logger.info("📨 Задача отправлена в Celery: %s", screenshot_ids)


class Command(BaseCommand):
    help = "Запускает watchdog для мониторинга папки со скриншотами"

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            type=str,
            default=None,
            help="Папка для мониторинга (по умолчанию WATCH_FOLDER из settings)",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        folder = options["folder"] or getattr(settings, "WATCH_FOLDER", None)

        if not folder:
            self.stderr.write("❌ Укажите WATCH_FOLDER в settings или передайте --folder")
            return

        if not os.path.isdir(folder):
            self.stderr.write(f"❌ Папка не существует: {folder}")
            return

        self.stdout.write(f"👁  Слежу за папкой: {folder}")
        self.stdout.write("Нажми Ctrl+C для остановки.")

        handler = ScreenshotHandler()
        observer = Observer()
        observer.schedule(handler, folder, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Остановка watchdog...")
            observer.stop()

        observer.join()
        self.stdout.write("✅ Watchdog остановлен.")

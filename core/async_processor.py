import logging
import threading
import queue
import time
from typing import Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisTask:
    task_id: str
    filename: str
    text: str
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    current_step: str = ""


class AnalysisQueue:
    def __init__(self, max_workers: int = 3):
        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, AnalysisTask] = {}
        self._lock = threading.Lock()
        self._shutdown = False
        logger.info(f"AnalysisQueue initialized with {max_workers} workers")

    def submit_analysis(
        self,
        filename: str,
        text: str,
        analysis_func: Callable[[str], Dict]
    ) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = AnalysisTask(
            task_id=task_id,
            filename=filename,
            text=text
        )

        with self._lock:
            self.tasks[task_id] = task

        future = self.executor.submit(
            self._run_analysis,
            task_id,
            text,
            analysis_func
        )
        task.future = future
        logger.info(f"Submitted analysis task: {task_id} for {filename}")
        return task_id

    def _run_analysis(
        self,
        task_id: str,
        text: str,
        analysis_func: Callable[[str], Dict]
    ):
        task = self.tasks.get(task_id)
        if not task:
            return

        try:
            task.status = "running"
            task.started_at = datetime.now()
            task.current_step = "Initializing analysis..."
            task.progress = 10

            result = analysis_func(text)

            task.progress = 100
            task.current_step = "Complete"
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now()

            logger.info(f"Analysis task completed: {task_id}")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Analysis task failed: {task_id} - {e}")

    def get_task_status(self, task_id: str) -> Optional[AnalysisTask]:
        return self.tasks.get(task_id)

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        task = self.tasks.get(task_id)
        if task and task.status == "completed":
            return task.result
        return None

    def is_task_complete(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        return task is not None and task.status in ("completed", "failed")

    def get_pending_tasks(self) -> list:
        return [t for t in self.tasks.values() if t.status == "pending"]

    def get_running_tasks(self) -> list:
        return [t for t in self.tasks.values() if t.status == "running"]

    def shutdown(self, wait: bool = True):
        self._shutdown = True
        self.executor.shutdown(wait=wait)
        logger.info("AnalysisQueue shutdown complete")


class AsyncAnalyzer:
    def __init__(self, max_workers: int = 3):
        self.queue = AnalysisQueue(max_workers=max_workers)
        self._analysis_func = None

    def set_analysis_function(self, func: Callable[[str], Dict]):
        self._analysis_func = func

    def analyze_async(
        self,
        filename: str,
        text: str
    ) -> str:
        if not self._analysis_func:
            raise ValueError("Analysis function not set")
        return self.queue.submit_analysis(filename, text, self._analysis_func)

    def get_status(self, task_id: str) -> Dict:
        task = self.queue.get_task_status(task_id)
        if not task:
            return {"error": "Task not found"}

        return {
            "task_id": task.task_id,
            "filename": task.filename,
            "status": task.status,
            "progress": task.progress,
            "current_step": task.current_step,
            "error": task.error,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

    def get_result(self, task_id: str) -> Optional[Dict]:
        return self.queue.get_task_result(task_id)

    def wait_for_completion(self, task_id: str, timeout: float = 300) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.queue.is_task_complete(task_id):
                return True
            time.sleep(0.5)
        return False


async_analyzer = AsyncAnalyzer(max_workers=2)


def analyze_document_async(text: str) -> Dict:
    import text_analyzer
    return text_analyzer.analyze_full_document(text)


async_analyzer.set_analysis_function(analyze_document_async)

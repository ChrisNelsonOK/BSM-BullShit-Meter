"""
Async Manager - Improved concurrency and threading management for BSM.

This module provides a clean separation between Qt's event loop and Python's asyncio,
with proper cancellation support, progress reporting, and error handling.
"""

import asyncio
import concurrent.futures
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Coroutine
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
from contextlib import asynccontextmanager
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TaskStatus(Enum):
    """Status of an async task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result of an async task execution."""
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[Exception] = None
    duration: float = 0.0


class AsyncTaskManager(QObject):
    """
    Manages async tasks with proper Qt integration.
    
    This class provides:
    - Clean separation of Qt and asyncio event loops
    - Progress reporting
    - Cancellation support
    - Timeout handling
    - Error propagation
    """
    
    # Signals
    progress_updated = pyqtSignal(str, int)  # task_id, progress (0-100)
    task_started = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, str)  # task_id, error_message
    task_cancelled = pyqtSignal(str)  # task_id
    
    def __init__(self):
        super().__init__()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self._tasks: Dict[str, asyncio.Task] = {}
        self._task_futures: Dict[str, concurrent.futures.Future] = {}
        self._shutdown = False
        
    def submit_async_task(
        self,
        task_id: str,
        coro_func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        timeout: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Submit an async task for execution.
        
        Args:
            task_id: Unique identifier for the task
            coro_func: Async function to execute
            *args: Positional arguments for the function
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for the function
        """
        if self._shutdown:
            self.task_failed.emit(task_id, "Task manager is shutting down")
            return
            
        if task_id in self._task_futures:
            self.task_failed.emit(task_id, f"Task {task_id} is already running")
            return
        
        # Submit to executor
        future = self._executor.submit(
            self._run_async_task,
            task_id,
            coro_func,
            args,
            kwargs,
            timeout
        )
        
        self._task_futures[task_id] = future
        self.task_started.emit(task_id)
        
        # Set up completion callback
        future.add_done_callback(
            functools.partial(self._handle_task_completion, task_id)
        )
    
    def _run_async_task(
        self,
        task_id: str,
        coro_func: Callable,
        args: tuple,
        kwargs: dict,
        timeout: Optional[float]
    ) -> TaskResult:
        """Run an async task in a new event loop."""
        start_time = time.time()
        
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create the coroutine
            coro = coro_func(*args, **kwargs)
            
            # Create task with timeout if specified
            if timeout:
                task = asyncio.create_task(
                    asyncio.wait_for(coro, timeout=timeout)
                )
            else:
                task = asyncio.create_task(coro)
            
            # Store task reference
            self._tasks[task_id] = task
            
            # Run until complete
            result = loop.run_until_complete(task)
            
            duration = time.time() - start_time
            return TaskResult(
                status=TaskStatus.COMPLETED,
                result=result,
                duration=duration
            )
            
        except asyncio.TimeoutError:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=TimeoutError(f"Task {task_id} timed out after {timeout}s"),
                duration=time.time() - start_time
            )
        except asyncio.CancelledError:
            return TaskResult(
                status=TaskStatus.CANCELLED,
                duration=time.time() - start_time
            )
        except Exception as e:
            logger.exception(f"Task {task_id} failed with error")
            return TaskResult(
                status=TaskStatus.FAILED,
                error=e,
                duration=time.time() - start_time
            )
        finally:
            # Clean up
            self._tasks.pop(task_id, None)
            loop.close()
    
    def _handle_task_completion(self, task_id: str, future: concurrent.futures.Future):
        """Handle task completion in Qt thread."""
        try:
            result = future.result()
            
            if result.status == TaskStatus.COMPLETED:
                self.task_completed.emit(task_id, result.result)
            elif result.status == TaskStatus.CANCELLED:
                self.task_cancelled.emit(task_id)
            else:
                error_msg = str(result.error) if result.error else "Unknown error"
                self.task_failed.emit(task_id, error_msg)
                
        except Exception as e:
            logger.exception(f"Error handling task {task_id} completion")
            self.task_failed.emit(task_id, str(e))
        finally:
            self._task_futures.pop(task_id, None)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Returns:
            True if cancellation was initiated, False if task not found
        """
        # Cancel the asyncio task
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.cancel()
            return True
            
        # Cancel the future
        if task_id in self._task_futures:
            future = self._task_futures[task_id]
            future.cancel()
            return True
            
        return False
    
    def cancel_all_tasks(self):
        """Cancel all running tasks."""
        for task_id in list(self._tasks.keys()):
            self.cancel_task(task_id)
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        return task_id in self._task_futures
    
    def update_progress(self, task_id: str, progress: int):
        """Update progress for a task (0-100)."""
        if 0 <= progress <= 100:
            self.progress_updated.emit(task_id, progress)
    
    def shutdown(self):
        """Shutdown the task manager and cleanup resources."""
        self._shutdown = True
        self.cancel_all_tasks()
        self._executor.shutdown(wait=True)


class CircuitBreaker:
    """
    Circuit breaker pattern for handling repeated failures.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failures exceeded threshold, blocking calls
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "CLOSED"
    
    @asynccontextmanager
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self._state == "OPEN":
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self._state == "HALF_OPEN":
                self._state = "CLOSED"
                self._failure_count = 0
            yield result
            
        except self.expected_exception as e:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.failure_threshold:
                self._state = "OPEN"
                logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            
            raise e


class RetryPolicy:
    """Retry policy with exponential backoff."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = min(
                        self.initial_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_attempts} attempts failed")
        
        raise last_exception


# Global instance for easy access
_task_manager: Optional[AsyncTaskManager] = None


def get_task_manager() -> AsyncTaskManager:
    """Get or create the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager()
    return _task_manager


def shutdown_task_manager():
    """Shutdown the global task manager."""
    global _task_manager
    if _task_manager:
        _task_manager.shutdown()
        _task_manager = None

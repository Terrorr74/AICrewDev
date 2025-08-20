#!/usr/bin/env python3
"""
Real-time Progress Monitoring Module

This module provides real-time progress tracking and live status updates
for LLM operations, giving users visibility into ongoing processes.
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
import json

class OperationStatus(str, Enum):
    """Status of an ongoing operation"""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    STREAMING = "streaming"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProgressUpdate:
    """Real-time progress update for an operation"""
    operation_id: str
    status: OperationStatus
    progress_percent: float
    current_step: str
    estimated_remaining_seconds: Optional[float] = None
    tokens_processed: int = 0
    tokens_per_second: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LiveOperation:
    """Represents a live operation being tracked"""
    operation_id: str
    operation_type: str
    start_time: datetime
    status: OperationStatus = OperationStatus.QUEUED
    progress_percent: float = 0.0
    current_step: str = "Initializing..."
    estimated_duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def estimated_remaining_seconds(self) -> Optional[float]:
        """Calculate estimated remaining time"""
        if self.progress_percent <= 0 or self.estimated_duration_seconds is None:
            return None
        
        elapsed = self.elapsed_seconds()
        if self.progress_percent >= 100:
            return 0.0
        
        estimated_total = elapsed / (self.progress_percent / 100)
        return max(0, estimated_total - elapsed)

class RealTimeMonitor:
    """
    Real-time monitoring system for tracking live operations
    and providing progress updates to users.
    """
    
    def __init__(self, update_interval_seconds: float = 0.5):
        self.update_interval = update_interval_seconds
        self.active_operations: Dict[str, LiveOperation] = {}
        self.progress_callbacks: List[Callable[[ProgressUpdate], None]] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Historical data for estimation
        self.operation_history: Dict[str, List[float]] = {}
        
    def add_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Add a callback to receive progress updates"""
        self.progress_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start the real-time monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the real-time monitoring thread"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def start_operation(self, operation_id: str, operation_type: str, 
                       estimated_duration: Optional[float] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> LiveOperation:
        """Start tracking a new operation"""
        with self._lock:
            operation = LiveOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                start_time=datetime.now(),
                estimated_duration_seconds=estimated_duration or self._estimate_duration(operation_type),
                metadata=metadata or {}
            )
            self.active_operations[operation_id] = operation
            
        self._notify_progress(operation_id)
        return operation
    
    def update_operation(self, operation_id: str, 
                        status: Optional[OperationStatus] = None,
                        progress_percent: Optional[float] = None,
                        current_step: Optional[str] = None,
                        tokens_processed: Optional[int] = None,
                        metadata: Optional[Dict[str, Any]] = None):
        """Update the progress of an ongoing operation"""
        with self._lock:
            if operation_id not in self.active_operations:
                return
                
            operation = self.active_operations[operation_id]
            
            if status is not None:
                operation.status = status
            if progress_percent is not None:
                operation.progress_percent = min(100.0, max(0.0, progress_percent))
            if current_step is not None:
                operation.current_step = current_step
            if tokens_processed is not None:
                operation.metadata['tokens_processed'] = tokens_processed
            if metadata:
                operation.metadata.update(metadata)
        
        self._notify_progress(operation_id)
    
    def complete_operation(self, operation_id: str, success: bool = True,
                          final_metadata: Optional[Dict[str, Any]] = None):
        """Mark an operation as completed"""
        with self._lock:
            if operation_id not in self.active_operations:
                return
                
            operation = self.active_operations[operation_id]
            operation.status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
            operation.progress_percent = 100.0
            operation.current_step = "Completed" if success else "Failed"
            
            if final_metadata:
                operation.metadata.update(final_metadata)
            
            # Store duration for future estimations
            duration = operation.elapsed_seconds()
            op_type = operation.operation_type
            if op_type not in self.operation_history:
                self.operation_history[op_type] = []
            self.operation_history[op_type].append(duration)
            
            # Keep only recent history (last 10 operations)
            self.operation_history[op_type] = self.operation_history[op_type][-10:]
        
        self._notify_progress(operation_id)
        
        # Remove from active operations after a delay
        threading.Timer(5.0, lambda: self._remove_operation(operation_id)).start()
    
    def get_active_operations(self) -> Dict[str, LiveOperation]:
        """Get all currently active operations"""
        with self._lock:
            return self.active_operations.copy()
    
    def get_operation_status(self, operation_id: str) -> Optional[LiveOperation]:
        """Get status of a specific operation"""
        with self._lock:
            return self.active_operations.get(operation_id)
    
    def _estimate_duration(self, operation_type: str) -> Optional[float]:
        """Estimate operation duration based on historical data"""
        if operation_type not in self.operation_history:
            # Default estimates based on operation type
            defaults = {
                "llm_chat": 5.0,
                "llm_completion": 10.0,
                "llm_generation": 15.0,
                "crew_execution": 30.0,
                "agent_task": 8.0
            }
            return defaults.get(operation_type)
        
        # Calculate average from recent history
        history = self.operation_history[operation_type]
        return sum(history) / len(history) if history else None
    
    def _notify_progress(self, operation_id: str):
        """Notify all callbacks about progress update"""
        with self._lock:
            operation = self.active_operations.get(operation_id)
            if not operation:
                return
            
            # Calculate tokens per second
            tokens_processed = operation.metadata.get('tokens_processed', 0)
            elapsed = operation.elapsed_seconds()
            tokens_per_second = tokens_processed / elapsed if elapsed > 0 else 0.0
            
            progress_update = ProgressUpdate(
                operation_id=operation_id,
                status=operation.status,
                progress_percent=operation.progress_percent,
                current_step=operation.current_step,
                estimated_remaining_seconds=operation.estimated_remaining_seconds(),
                tokens_processed=tokens_processed,
                tokens_per_second=tokens_per_second,
                metadata=operation.metadata.copy()
            )
        
        # Call callbacks outside of lock to avoid deadlocks
        for callback in self.progress_callbacks:
            try:
                callback(progress_update)
            except Exception as e:
                print(f"Error in progress callback: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        while self.is_monitoring:
            try:
                # Update all active operations
                with self._lock:
                    operation_ids = list(self.active_operations.keys())
                
                for operation_id in operation_ids:
                    self._notify_progress(operation_id)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _remove_operation(self, operation_id: str):
        """Remove an operation from active tracking"""
        with self._lock:
            self.active_operations.pop(operation_id, None)

class ProgressDisplayManager:
    """
    Manages the display of progress information in various formats
    (console, web, JSON, etc.)
    """
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.monitor.add_progress_callback(self._on_progress_update)
        self.display_enabled = True
        
    def enable_console_display(self):
        """Enable console progress display"""
        self.display_enabled = True
        
    def disable_console_display(self):
        """Disable console progress display"""
        self.display_enabled = False
    
    def _on_progress_update(self, update: ProgressUpdate):
        """Handle progress updates"""
        if not self.display_enabled:
            return
            
        self._display_console_progress(update)
    
    def _display_console_progress(self, update: ProgressUpdate):
        """Display progress in console format"""
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * update.progress_percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Format remaining time
        remaining_str = ""
        if update.estimated_remaining_seconds is not None:
            if update.estimated_remaining_seconds < 60:
                remaining_str = f" (ETA: {update.estimated_remaining_seconds:.1f}s)"
            else:
                minutes = int(update.estimated_remaining_seconds // 60)
                seconds = int(update.estimated_remaining_seconds % 60)
                remaining_str = f" (ETA: {minutes}m {seconds}s)"
        
        # Format tokens per second
        tps_str = ""
        if update.tokens_per_second > 0:
            tps_str = f" | {update.tokens_per_second:.1f} tok/s"
        
        # Status emoji
        status_emoji = {
            OperationStatus.QUEUED: "⏳",
            OperationStatus.INITIALIZING: "🔄",
            OperationStatus.PROCESSING: "⚙️",
            OperationStatus.STREAMING: "📡",
            OperationStatus.FINALIZING: "🔄",
            OperationStatus.COMPLETED: "✅",
            OperationStatus.FAILED: "❌",
            OperationStatus.CANCELLED: "⏹️"
        }.get(update.status, "🔄")
        
        # Print progress line
        print(f"\r{status_emoji} [{bar}] {update.progress_percent:5.1f}% | {update.current_step}{remaining_str}{tps_str}", 
              end="", flush=True)
        
        # Print newline when completed
        if update.status in [OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.CANCELLED]:
            print()  # New line
    
    def get_progress_json(self, operation_id: Optional[str] = None) -> str:
        """Get progress information as JSON"""
        if operation_id:
            operation = self.monitor.get_operation_status(operation_id)
            if operation:
                return json.dumps({
                    "operation_id": operation_id,
                    "status": operation.status.value,
                    "progress_percent": operation.progress_percent,
                    "current_step": operation.current_step,
                    "elapsed_seconds": operation.elapsed_seconds(),
                    "estimated_remaining_seconds": operation.estimated_remaining_seconds(),
                    "metadata": operation.metadata
                }, indent=2)
        else:
            operations = self.monitor.get_active_operations()
            return json.dumps({
                op_id: {
                    "status": op.status.value,
                    "progress_percent": op.progress_percent,
                    "current_step": op.current_step,
                    "elapsed_seconds": op.elapsed_seconds(),
                    "estimated_remaining_seconds": op.estimated_remaining_seconds(),
                    "metadata": op.metadata
                }
                for op_id, op in operations.items()
            }, indent=2)
        
        return "{}"

# Global instance for easy access
_global_monitor = None
_global_display_manager = None

def get_global_monitor() -> RealTimeMonitor:
    """Get the global real-time monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RealTimeMonitor()
        _global_monitor.start_monitoring()
    return _global_monitor

def get_global_display_manager() -> ProgressDisplayManager:
    """Get the global progress display manager"""
    global _global_display_manager
    if _global_display_manager is None:
        _global_display_manager = ProgressDisplayManager(get_global_monitor())
    return _global_display_manager

def track_operation(operation_id: str, operation_type: str, 
                   estimated_duration: Optional[float] = None):
    """Decorator for tracking operation progress"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_global_monitor()
            operation = monitor.start_operation(operation_id, operation_type, estimated_duration)
            
            try:
                monitor.update_operation(operation_id, 
                                       status=OperationStatus.PROCESSING,
                                       current_step="Executing...")
                result = func(*args, **kwargs)
                monitor.complete_operation(operation_id, success=True)
                return result
            except Exception as e:
                monitor.complete_operation(operation_id, success=False,
                                         final_metadata={"error": str(e)})
                raise
        
        return wrapper
    return decorator

# Export main classes and functions
__all__ = [
    "RealTimeMonitor", "ProgressDisplayManager", "OperationStatus", 
    "ProgressUpdate", "LiveOperation", "get_global_monitor", 
    "get_global_display_manager", "track_operation"
]

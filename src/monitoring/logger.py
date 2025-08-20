"""
Enhanced structured logging system for AICrewDev.

Provides contextual logging with structured data, log levels, and proper formatting
for production environments and debugging.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path

# Import real-time monitoring
try:
    from .real_time_monitor import get_global_monitor, OperationStatus
    REAL_TIME_MONITORING_AVAILABLE = True
except ImportError:
    REAL_TIME_MONITORING_AVAILABLE = False

class LogLevel(Enum):
    """Log levels for structured logging."""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AICrewLogger:
    """
    Enhanced structured logger for AICrewDev with context preservation.
    
    Features:
    - Structured JSON logging for production
    - Context preservation across operations
    - Performance tracking
    - Error correlation
    - Configurable output formats
    """
    
    def __init__(
        self, 
        service_name: str = "aicrewdev",
        environment: str = "development",
        log_level: Union[str, LogLevel] = LogLevel.INFO,
        enable_console: bool = True,
        enable_file: bool = True,
        log_file_path: Optional[str] = None
    ):
        """
        Initialize the structured logger.
        
        Args:
            service_name: Name of the service (for correlation)
            environment: Environment (development, production, testing)
            log_level: Minimum log level to output
            enable_console: Whether to log to console
            enable_file: Whether to log to file
            log_file_path: Custom log file path
        """
        self.service_name = service_name
        self.environment = environment
        self.log_level = log_level if isinstance(log_level, LogLevel) else LogLevel(log_level)
        
        # Create logger instance
        self.logger = logging.getLogger(f"{service_name}.{environment}")
        self.logger.setLevel(getattr(logging, self.log_level.value))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup formatters
        self._setup_formatters()
        
        # Setup handlers
        if enable_console:
            self._setup_console_handler()
        
        if enable_file:
            self._setup_file_handler(log_file_path)
        
        # Context storage
        self.context = {
            "service": service_name,
            "environment": environment,
            "pid": str(os.getpid()) if 'os' in globals() else "unknown"
        }
    
    def _setup_formatters(self):
        """Setup log formatters for different outputs."""
        # JSON formatter for production/file logging
        self.json_formatter = logging.Formatter(
            '%(message)s'  # We'll format the JSON ourselves
        )
        
        # Human-readable formatter for console/development
        self.console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _setup_console_handler(self):
        """Setup console handler with appropriate formatting."""
        console_handler = logging.StreamHandler()
        
        if self.environment == "production":
            console_handler.setFormatter(self.json_formatter)
        else:
            console_handler.setFormatter(self.console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, log_file_path: Optional[str] = None):
        """Setup file handler with JSON formatting."""
        if not log_file_path:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_file_path = str(log_dir / f"{self.service_name}_{self.environment}.log")
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(self.json_formatter)
        self.logger.addHandler(file_handler)
    
    def _create_log_entry(
        self, 
        level: str, 
        message: str, 
        extra_context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error: Optional[Exception] = None
    ) -> str:
        """Create structured log entry."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        log_entry: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": level,
            "service": self.service_name,
            "environment": self.environment,
            "message": message,
            **self.context
        }
        
        # Add operation context
        if operation:
            log_entry["operation"] = operation
        
        # Add performance data
        if duration_ms is not None:
            log_entry["duration_ms"] = round(duration_ms, 2)
        
        # Add error information
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": self._get_error_traceback(error)
            }
        
        # Add extra context
        if extra_context:
            log_entry.update(extra_context)
        
        if self.environment == "production":
            return json.dumps(log_entry, ensure_ascii=False)
        else:
            # Format for human readability in development
            context_str = ""
            if extra_context or operation or duration_ms:
                context_parts = []
                if operation:
                    context_parts.append(f"op={operation}")
                if duration_ms is not None:
                    context_parts.append(f"duration={duration_ms:.2f}ms")
                if extra_context:
                    for k, v in extra_context.items():
                        context_parts.append(f"{k}={v}")
                context_str = f" [{', '.join(context_parts)}]"
            
            return f"{message}{context_str}"
    
    def _get_error_traceback(self, error: Exception) -> str:
        """Get formatted traceback for error."""
        import traceback
        return '\n'.join(traceback.format_exception(type(error), error, error.__traceback__))
    
    def add_context(self, **kwargs):
        """Add persistent context to all log messages."""
        self.context.update(kwargs)
    
    def remove_context(self, *keys):
        """Remove context keys."""
        for key in keys:
            self.context.pop(key, None)
    
    def clear_context(self):
        """Clear all context except service defaults."""
        service = self.context.get("service")
        environment = self.context.get("environment")
        pid = self.context.get("pid")
        
        self.context.clear()
        if service:
            self.context["service"] = service
        if environment:
            self.context["environment"] = environment
        if pid:
            self.context["pid"] = pid
    
    # Core logging methods
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        log_entry = self._create_log_entry("DEBUG", message, kwargs)
        self.logger.debug(log_entry)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        log_entry = self._create_log_entry("INFO", message, kwargs)
        self.logger.info(log_entry)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        log_entry = self._create_log_entry("WARNING", message, kwargs)
        self.logger.warning(log_entry)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception context."""
        log_entry = self._create_log_entry("ERROR", message, kwargs, error=error)
        self.logger.error(log_entry)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception context."""
        log_entry = self._create_log_entry("CRITICAL", message, kwargs, error=error)
        self.logger.critical(log_entry)
    
    # Domain-specific logging methods
    def log_agent_action(
        self, 
        agent_id: str, 
        action: str, 
        context: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        success: bool = True
    ):
        """
        Log agent action with structured context.
        
        Args:
            agent_id: Unique agent identifier
            action: Action being performed
            context: Additional context data
            duration_ms: Action duration in milliseconds
            success: Whether action was successful
        """
        log_context = {
            "component": "agent",
            "agent_id": agent_id,
            "action": action,
            "success": success
        }
        
        if context:
            log_context.update(context)
        
        message = f"Agent {agent_id} performed {action}"
        if success:
            self.info(message, operation="agent_action", duration_ms=duration_ms, **log_context)
        else:
            self.warning(message, operation="agent_action", duration_ms=duration_ms, **log_context)
    
    def log_crew_execution(
        self, 
        crew_id: str, 
        execution_data: Dict[str, Any],
        duration_ms: Optional[float] = None,
        success: bool = True
    ):
        """
        Log crew execution with detailed context.
        
        Args:
            crew_id: Unique crew identifier
            execution_data: Execution context and results
            duration_ms: Execution duration in milliseconds
            success: Whether execution was successful
        """
        log_context = {
            "component": "crew",
            "crew_id": crew_id,
            "success": success,
            **execution_data
        }
        
        message = f"Crew {crew_id} execution {'completed' if success else 'failed'}"
        
        if success:
            self.info(message, operation="crew_execution", duration_ms=duration_ms, **log_context)
        else:
            self.error(message, operation="crew_execution", duration_ms=duration_ms, **log_context)
    
    def log_llm_interaction(
        self,
        provider: str,
        model: str,
        operation: str,
        tokens_used: Optional[int] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[Exception] = None,
        operation_id: Optional[str] = None
    ):
        """
        Log LLM interaction with usage metrics and real-time tracking.
        
        Args:
            provider: LLM provider (openai, anthropic, ollama, etc.)
            model: Model name
            operation: Operation type (chat, completion, etc.)
            tokens_used: Number of tokens consumed
            duration_ms: Request duration in milliseconds
            success: Whether request was successful
            error: Exception if request failed
            operation_id: Optional operation ID for real-time tracking
        """
        log_context = {
            "component": "llm",
            "provider": provider,
            "model": model,
            "llm_operation": operation,
            "success": success
        }
        
        if tokens_used:
            log_context["tokens_used"] = tokens_used
        
        # Update real-time monitoring if available and operation_id provided
        if REAL_TIME_MONITORING_AVAILABLE and operation_id:
            try:
                monitor = get_global_monitor()
                if success:
                    monitor.update_operation(
                        operation_id,
                        status=OperationStatus.COMPLETED,
                        progress_percent=100.0,
                        current_step="LLM response received",
                        tokens_processed=tokens_used or 0,
                        metadata={"provider": provider, "model": model}
                    )
                else:
                    monitor.update_operation(
                        operation_id,
                        status=OperationStatus.FAILED,
                        current_step=f"LLM request failed: {error}" if error else "LLM request failed"
                    )
            except Exception as e:
                # Don't let monitoring errors break the main logging
                pass
        
        message = f"LLM {provider}/{model} {operation}"
        
        if success:
            self.info(message, operation="llm_interaction", duration_ms=duration_ms, **log_context)
        else:
            self.error(message, operation="llm_interaction", duration_ms=duration_ms, 
                      error=error, **log_context)
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Log performance metric for monitoring.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags for metric categorization
        """
        log_context = {
            "component": "metrics",
            "metric_name": metric_name,
            "value": value,
            "unit": unit
        }
        
        if tags:
            log_context.update(tags)
        
        message = f"Metric: {metric_name}={value}{unit}"
        self.info(message, operation="performance_metric", **log_context)
    
    def log_configuration_change(
        self,
        component: str,
        old_value: Any,
        new_value: Any,
        changed_by: Optional[str] = None
    ):
        """
        Log configuration changes for audit trail.
        
        Args:
            component: Component being configured
            old_value: Previous value
            new_value: New value
            changed_by: Who made the change
        """
        log_context = {
            "component": "configuration",
            "config_component": component,
            "old_value": str(old_value),
            "new_value": str(new_value)
        }
        
        if changed_by:
            log_context["changed_by"] = changed_by
        
        message = f"Configuration changed: {component}"
        self.info(message, operation="config_change", **log_context)


# Performance logging decorator
def log_performance(logger: AICrewLogger, operation: str):
    """
    Decorator to automatically log operation performance.
    
    Args:
        logger: AICrewLogger instance
        operation: Operation name for logging
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Operation {operation} completed",
                    operation=operation,
                    duration_ms=duration_ms,
                    success=True
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Operation {operation} failed",
                    operation=operation,
                    duration_ms=duration_ms,
                    error=e,
                    success=False
                )
                raise
        return wrapper
    return decorator


# Import for traceback formatting
import os

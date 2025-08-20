"""
Metrics collection and performance monitoring for AICrewDev.

Tracks performance metrics, usage statistics, and system health indicators
for monitoring and optimization purposes.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import threading
import json

class MetricType(Enum):
    """Types of metrics we can collect."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class PerformanceStats:
    """Performance statistics for an operation."""
    operation: str
    total_executions: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    last_execution: Optional[datetime] = None

@dataclass
class LLMUsageStats:
    """LLM usage statistics."""
    provider: str
    model: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_tokens_per_request: float = 0.0
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0

class MetricsCollector:
    """
    Real-time metrics collection and analysis for AICrewDev.
    
    Features:
    - Performance tracking for all operations
    - LLM usage and cost monitoring
    - System health metrics
    - Real-time dashboard data
    - Historical trend analysis
    - Alerting thresholds
    """
    
    def __init__(self, retention_hours: int = 24, max_datapoints: int = 10000):
        """
        Initialize metrics collector.
        
        Args:
            retention_hours: How long to retain metrics data
            max_datapoints: Maximum number of data points to keep
        """
        self.retention_hours = retention_hours
        self.max_datapoints = max_datapoints
        
        # Thread-safe metrics storage
        self._lock = threading.Lock()
        
        # Raw metrics storage
        self._metrics: deque = deque(maxlen=max_datapoints)
        
        # Aggregated statistics
        self._performance_stats: Dict[str, PerformanceStats] = {}
        self._llm_usage_stats: Dict[str, LLMUsageStats] = defaultdict(lambda: LLMUsageStats("", ""))
        
        # System metrics
        self._system_metrics: Dict[str, Any] = {}
        
        # Custom counters and gauges
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        
        # Time series data for trending
        self._time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Error tracking
        self._error_patterns: Dict[str, int] = defaultdict(int)
        
        # Start time for uptime calculation
        self._start_time = datetime.utcnow()
    
    def _add_metric(self, metric: MetricPoint):
        """Thread-safe metric addition."""
        with self._lock:
            self._metrics.append(metric)
            
            # Add to time series
            series_key = f"{metric.name}_{metric.metric_type.value}"
            self._time_series[series_key].append({
                "timestamp": metric.timestamp,
                "value": metric.value,
                "tags": metric.tags
            })
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # Clean up main metrics
            while self._metrics and self._metrics[0].timestamp < cutoff_time:
                self._metrics.popleft()
            
            # Clean up time series
            for series in self._time_series.values():
                while series and series[0]["timestamp"] < cutoff_time:
                    series.popleft()
    
    # Performance tracking methods
    def track_operation_start(self, operation: str) -> str:
        """
        Start tracking an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Unique tracking ID for this operation
        """
        tracking_id = f"{operation}_{int(time.time() * 1000000)}"
        
        metric = MetricPoint(
            name="operation_started",
            value=1,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow(),
            tags={"operation": operation, "tracking_id": tracking_id}
        )
        
        self._add_metric(metric)
        self.increment_counter(f"operations_started_{operation}")
        
        return tracking_id
    
    def track_operation_end(
        self, 
        operation: str, 
        tracking_id: str, 
        duration_ms: float, 
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """
        End tracking an operation and record performance.
        
        Args:
            operation: Operation name
            tracking_id: Tracking ID from start
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
            error_type: Type of error if failed
        """
        # Record timing metric
        metric = MetricPoint(
            name="operation_duration_ms",
            value=duration_ms,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            tags={
                "operation": operation,
                "tracking_id": tracking_id,
                "success": str(success),
                "error_type": error_type or "none"
            }
        )
        
        self._add_metric(metric)
        
        # Update performance statistics
        with self._lock:
            if operation not in self._performance_stats:
                self._performance_stats[operation] = PerformanceStats(operation)
            
            stats = self._performance_stats[operation]
            stats.total_executions += 1
            stats.total_duration_ms += duration_ms
            stats.min_duration_ms = min(stats.min_duration_ms, duration_ms)
            stats.max_duration_ms = max(stats.max_duration_ms, duration_ms)
            stats.avg_duration_ms = stats.total_duration_ms / stats.total_executions
            stats.last_execution = datetime.utcnow()
            
            if success:
                stats.success_count += 1
            else:
                stats.error_count += 1
                if error_type:
                    self._error_patterns[f"{operation}_{error_type}"] += 1
            
            stats.success_rate = stats.success_count / stats.total_executions
        
        # Update counters
        if success:
            self.increment_counter(f"operations_succeeded_{operation}")
        else:
            self.increment_counter(f"operations_failed_{operation}")
    
    def track_agent_performance(
        self, 
        agent_id: str, 
        agent_role: str,
        task_type: str,
        duration_ms: float,
        tokens_used: int = 0,
        success: bool = True,
        quality_score: Optional[float] = None
    ):
        """
        Track individual agent performance metrics.
        
        Args:
            agent_id: Unique agent identifier
            agent_role: Agent role (tech_lead, developer, etc.)
            task_type: Type of task performed
            duration_ms: Task duration in milliseconds
            tokens_used: LLM tokens consumed
            success: Whether task succeeded
            quality_score: Optional quality assessment (0-1)
        """
        tags = {
            "agent_id": agent_id,
            "agent_role": agent_role,
            "task_type": task_type,
            "success": str(success)
        }
        
        # Duration metric
        self._add_metric(MetricPoint(
            name="agent_task_duration_ms",
            value=duration_ms,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="ms"
        ))
        
        # Token usage metric
        if tokens_used > 0:
            self._add_metric(MetricPoint(
                name="agent_tokens_used",
                value=tokens_used,
                metric_type=MetricType.COUNTER,
                timestamp=datetime.utcnow(),
                tags=tags,
                unit="tokens"
            ))
        
        # Quality score metric
        if quality_score is not None:
            self._add_metric(MetricPoint(
                name="agent_quality_score",
                value=quality_score,
                metric_type=MetricType.GAUGE,
                timestamp=datetime.utcnow(),
                tags=tags,
                unit="score"
            ))
        
        # Update counters
        self.increment_counter(f"agent_tasks_{agent_role}")
        if success:
            self.increment_counter(f"agent_tasks_succeeded_{agent_role}")
        else:
            self.increment_counter(f"agent_tasks_failed_{agent_role}")
    
    def track_llm_usage(
        self, 
        provider: str, 
        model: str, 
        operation: str,
        tokens_used: int, 
        duration_ms: float,
        cost_usd: float = 0.0,
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """
        Track LLM usage and costs.
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
            operation: Operation type (chat, completion, etc.)
            tokens_used: Number of tokens consumed
            duration_ms: Request duration in milliseconds
            cost_usd: Cost in USD
            success: Whether request succeeded
            error_type: Type of error if failed
        """
        tags = {
            "provider": provider,
            "model": model,
            "operation": operation,
            "success": str(success),
            "error_type": error_type or "none"
        }
        
        # Usage metrics
        self._add_metric(MetricPoint(
            name="llm_tokens_used",
            value=tokens_used,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="tokens"
        ))
        
        self._add_metric(MetricPoint(
            name="llm_request_duration_ms",
            value=duration_ms,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="ms"
        ))
        
        if cost_usd > 0:
            self._add_metric(MetricPoint(
                name="llm_cost_usd",
                value=cost_usd,
                metric_type=MetricType.COUNTER,
                timestamp=datetime.utcnow(),
                tags=tags,
                unit="usd"
            ))
        
        # Update LLM usage statistics
        key = f"{provider}_{model}"
        with self._lock:
            stats = self._llm_usage_stats[key]
            if not stats.provider:  # Initialize if new
                stats.provider = provider
                stats.model = model
            
            stats.total_requests += 1
            stats.total_tokens += tokens_used
            stats.total_cost_usd += cost_usd
            stats.avg_tokens_per_request = stats.total_tokens / stats.total_requests
            
            if success:
                stats.success_count += 1
            else:
                stats.error_count += 1
            
            stats.success_rate = stats.success_count / stats.total_requests
    
    def track_crew_execution(
        self,
        crew_id: str,
        agents_count: int,
        tasks_count: int,
        duration_ms: float,
        success: bool = True,
        result_length: int = 0
    ):
        """
        Track crew execution metrics.
        
        Args:
            crew_id: Unique crew identifier
            agents_count: Number of agents in crew
            tasks_count: Number of tasks executed
            duration_ms: Total execution duration
            success: Whether execution succeeded
            result_length: Length of result output
        """
        tags = {
            "crew_id": crew_id,
            "success": str(success)
        }
        
        # Execution metrics
        self._add_metric(MetricPoint(
            name="crew_execution_duration_ms",
            value=duration_ms,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="ms"
        ))
        
        self._add_metric(MetricPoint(
            name="crew_agents_count",
            value=agents_count,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="agents"
        ))
        
        self._add_metric(MetricPoint(
            name="crew_tasks_count",
            value=tasks_count,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            tags=tags,
            unit="tasks"
        ))
        
        if result_length > 0:
            self._add_metric(MetricPoint(
                name="crew_result_length",
                value=result_length,
                metric_type=MetricType.GAUGE,
                timestamp=datetime.utcnow(),
                tags=tags,
                unit="chars"
            ))
        
        # Update counters
        self.increment_counter("crew_executions_total")
        if success:
            self.increment_counter("crew_executions_succeeded")
        else:
            self.increment_counter("crew_executions_failed")
    
    # System metrics
    def track_system_metric(self, name: str, value: Union[int, float], unit: str = ""):
        """Track system-level metrics like memory, CPU, etc."""
        self._add_metric(MetricPoint(
            name=f"system_{name}",
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            unit=unit
        ))
        
        self._system_metrics[name] = value
    
    # Counter and gauge operations
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] += value
        
        self._add_metric(MetricPoint(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow()
        ))
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge metric value."""
        with self._lock:
            self._gauges[name] = value
        
        self._add_metric(MetricPoint(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow()
        ))
    
    # Data retrieval methods
    def get_performance_stats(self, operation: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics for operations."""
        with self._lock:
            if operation:
                stats = self._performance_stats.get(operation)
                return {operation: stats} if stats else {}
            return dict(self._performance_stats)
    
    def get_llm_usage_stats(self) -> Dict[str, LLMUsageStats]:
        """Get LLM usage statistics."""
        with self._lock:
            return dict(self._llm_usage_stats)
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counter values."""
        with self._lock:
            return dict(self._counters)
    
    def get_gauges(self) -> Dict[str, float]:
        """Get all gauge values."""
        with self._lock:
            return dict(self._gauges)
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Get error pattern frequency."""
        with self._lock:
            return dict(self._error_patterns)
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive performance dashboard data.
        
        Returns:
            Dictionary with all key performance indicators
        """
        self._cleanup_old_metrics()
        
        with self._lock:
            # Calculate uptime
            uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
            
            # Top operations by frequency
            top_operations = sorted(
                [(op, stats.total_executions) for op, stats in self._performance_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Overall success rate
            total_successes = sum(stats.success_count for stats in self._performance_stats.values())
            total_executions = sum(stats.total_executions for stats in self._performance_stats.values())
            overall_success_rate = total_successes / total_executions if total_executions > 0 else 0
            
            # LLM usage summary
            total_llm_requests = sum(stats.total_requests for stats in self._llm_usage_stats.values())
            total_llm_tokens = sum(stats.total_tokens for stats in self._llm_usage_stats.values())
            total_llm_cost = sum(stats.total_cost_usd for stats in self._llm_usage_stats.values())
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": uptime_seconds,
                "system": {
                    "metrics_count": len(self._metrics),
                    "operations_tracked": len(self._performance_stats),
                    "system_metrics": dict(self._system_metrics)
                },
                "performance": {
                    "overall_success_rate": round(overall_success_rate, 3),
                    "total_executions": total_executions,
                    "total_successes": total_successes,
                    "top_operations": top_operations,
                    "operation_stats": {
                        name: {
                            "executions": stats.total_executions,
                            "avg_duration_ms": round(stats.avg_duration_ms, 2),
                            "success_rate": round(stats.success_rate, 3),
                            "last_execution": stats.last_execution.isoformat() if stats.last_execution else None
                        }
                        for name, stats in self._performance_stats.items()
                    }
                },
                "llm_usage": {
                    "total_requests": total_llm_requests,
                    "total_tokens": total_llm_tokens,
                    "total_cost_usd": round(total_llm_cost, 4),
                    "avg_tokens_per_request": round(total_llm_tokens / total_llm_requests, 1) if total_llm_requests > 0 else 0,
                    "provider_breakdown": {
                        key: {
                            "requests": stats.total_requests,
                            "tokens": stats.total_tokens,
                            "cost_usd": round(stats.total_cost_usd, 4),
                            "success_rate": round(stats.success_rate, 3)
                        }
                        for key, stats in self._llm_usage_stats.items()
                    }
                },
                "errors": {
                    "error_patterns": dict(self._error_patterns),
                    "total_errors": sum(self._error_patterns.values())
                },
                "counters": dict(self._counters),
                "gauges": dict(self._gauges)
            }
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format (json, csv, prometheus)
            
        Returns:
            Formatted metrics data
        """
        if format == "json":
            return json.dumps(self.get_performance_dashboard(), indent=2, default=str)
        elif format == "prometheus":
            # Basic Prometheus format
            lines = []
            
            # Counters
            for name, value in self._counters.items():
                lines.append(f"aicrewdev_{name} {value}")
            
            # Gauges
            for name, value in self._gauges.items():
                lines.append(f"aicrewdev_{name} {value}")
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._metrics.clear()
            self._performance_stats.clear()
            self._llm_usage_stats.clear()
            self._system_metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._time_series.clear()
            self._error_patterns.clear()
            self._start_time = datetime.utcnow()


# Context manager for automatic performance tracking
class PerformanceTracker:
    """Context manager for automatic operation performance tracking."""
    
    def __init__(self, metrics_collector: MetricsCollector, operation: str):
        self.metrics_collector = metrics_collector
        self.operation = operation
        self.tracking_id: Optional[str] = None
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.tracking_id = self.metrics_collector.track_operation_start(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None and self.tracking_id is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            success = exc_type is None
            error_type = exc_type.__name__ if exc_type else None
            
            self.metrics_collector.track_operation_end(
                self.operation,
                self.tracking_id,
                duration_ms,
                success,
                error_type
            )

"""
System health monitoring and diagnostics for AICrewDev.

Provides health checks for system components, connectivity monitoring,
and resource usage tracking for operational insights.
"""

import os
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any]

@dataclass
class SystemResources:
    """System resource usage information."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    load_average: Tuple[float, float, float]
    process_count: int

class HealthChecker:
    """
    System health monitoring and diagnostics for AICrewDev.
    
    Features:
    - LLM provider connectivity checks
    - System resource monitoring
    - Agent responsiveness testing
    - Configuration validation
    - Performance threshold monitoring
    """
    
    def __init__(
        self,
        check_interval_seconds: int = 60,
        timeout_seconds: int = 10,
        max_workers: int = 5
    ):
        """
        Initialize health checker.
        
        Args:
            check_interval_seconds: How often to run automatic checks
            timeout_seconds: Timeout for individual health checks
            max_workers: Maximum concurrent health check workers
        """
        self.check_interval_seconds = check_interval_seconds
        self.timeout_seconds = timeout_seconds
        self.max_workers = max_workers
        
        # Health check history
        self._health_history: List[HealthCheck] = []
        self._last_check_time: Optional[datetime] = None
        
        # Configuration for LLM endpoints
        self._llm_endpoints = {
            "openai": "https://api.openai.com/v1/models",
            "anthropic": "https://api.anthropic.com/v1/messages",
            # Note: Ollama would be local, so we'll check differently
        }
        
        # Performance thresholds
        self._thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "response_time_warning": 5000.0,  # ms
            "response_time_critical": 10000.0,  # ms
        }
    
    def set_threshold(self, metric: str, value: float):
        """Set performance threshold for health checks."""
        self._thresholds[metric] = value
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current performance thresholds."""
        return self._thresholds.copy()
    
    def check_system_resources(self) -> HealthCheck:
        """
        Check system resource usage.
        
        Returns:
            HealthCheck with system resource status
        """
        start_time = time.time()
        
        try:
            if not PSUTIL_AVAILABLE:
                duration_ms = (time.time() - start_time) * 1000
                return HealthCheck(
                    name="system_resources",
                    status=HealthStatus.WARNING,
                    message="psutil not available - install with: pip install psutil",
                    timestamp=datetime.utcnow(),
                    duration_ms=duration_ms,
                    details={"psutil_available": False}
                )
            
            # Get system resource information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0.0, 0.0, 0.0)
            process_count = len(psutil.pids())
            
            resources = SystemResources(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.used / disk.total * 100,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                load_average=load_avg,
                process_count=process_count
            )
            
            # Determine health status
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent >= self._thresholds["cpu_critical"]:
                status = HealthStatus.CRITICAL
                issues.append(f"CPU usage critical: {cpu_percent:.1f}%")
            elif cpu_percent >= self._thresholds["cpu_warning"]:
                status = HealthStatus.WARNING
                issues.append(f"CPU usage high: {cpu_percent:.1f}%")
            
            if memory.percent >= self._thresholds["memory_critical"]:
                status = HealthStatus.CRITICAL
                issues.append(f"Memory usage critical: {memory.percent:.1f}%")
            elif memory.percent >= self._thresholds["memory_warning"]:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                issues.append(f"Memory usage high: {memory.percent:.1f}%")
            
            disk_usage_percent = disk.used / disk.total * 100
            if disk_usage_percent >= self._thresholds["disk_critical"]:
                status = HealthStatus.CRITICAL
                issues.append(f"Disk usage critical: {disk_usage_percent:.1f}%")
            elif disk_usage_percent >= self._thresholds["disk_warning"]:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                issues.append(f"Disk usage high: {disk_usage_percent:.1f}%")
            
            message = "System resources healthy" if not issues else "; ".join(issues)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": resources.memory_available_mb,
                    "disk_usage_percent": disk_usage_percent,
                    "disk_free_gb": resources.disk_free_gb,
                    "load_average": load_avg,
                    "process_count": process_count
                }
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check system resources: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={"error": str(e)}
            )
    
    def check_llm_connectivity(self, provider: str, api_key: Optional[str] = None) -> HealthCheck:
        """
        Check connectivity to LLM provider.
        
        Args:
            provider: LLM provider name (openai, anthropic, ollama)
            api_key: API key for authentication
            
        Returns:
            HealthCheck with connectivity status
        """
        start_time = time.time()
        
        try:
            if provider == "ollama":
                # Check local Ollama installation
                return self._check_ollama_connectivity()
            
            if provider not in self._llm_endpoints:
                duration_ms = (time.time() - start_time) * 1000
                return HealthCheck(
                    name=f"llm_connectivity_{provider}",
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown provider: {provider}",
                    timestamp=datetime.utcnow(),
                    duration_ms=duration_ms,
                    details={"provider": provider}
                )
            
            # Check API connectivity
            endpoint = self._llm_endpoints[provider]
            headers = {}
            
            if provider == "openai" and api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "anthropic" and api_key:
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
            
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=self.timeout_seconds
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine status based on response
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = f"{provider} API is accessible"
            elif response.status_code == 401:
                status = HealthStatus.WARNING
                message = f"{provider} API authentication failed (check API key)"
            elif response.status_code >= 500:
                status = HealthStatus.CRITICAL
                message = f"{provider} API server error (status: {response.status_code})"
            else:
                status = HealthStatus.WARNING
                message = f"{provider} API returned status {response.status_code}"
            
            return HealthCheck(
                name=f"llm_connectivity_{provider}",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "provider": provider,
                    "status_code": response.status_code,
                    "response_time_ms": duration_ms,
                    "endpoint": endpoint
                }
            )
            
        except requests.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=f"llm_connectivity_{provider}",
                status=HealthStatus.CRITICAL,
                message=f"{provider} API unreachable: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "provider": provider,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=f"llm_connectivity_{provider}",
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={"error": str(e)}
            )
    
    def _check_ollama_connectivity(self) -> HealthCheck:
        """Check local Ollama connectivity."""
        start_time = time.time()
        
        try:
            # Try to connect to local Ollama instance
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=self.timeout_seconds
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return HealthCheck(
                    name="llm_connectivity_ollama",
                    status=HealthStatus.HEALTHY,
                    message=f"Ollama is running with {len(models)} models",
                    timestamp=datetime.utcnow(),
                    duration_ms=duration_ms,
                    details={
                        "provider": "ollama",
                        "models_count": len(models),
                        "models": [model.get("name", "") for model in models[:5]]  # First 5 models
                    }
                )
            else:
                return HealthCheck(
                    name="llm_connectivity_ollama",
                    status=HealthStatus.CRITICAL,
                    message=f"Ollama returned status {response.status_code}",
                    timestamp=datetime.utcnow(),
                    duration_ms=duration_ms,
                    details={"provider": "ollama", "status_code": response.status_code}
                )
                
        except requests.RequestException:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="llm_connectivity_ollama",
                status=HealthStatus.CRITICAL,
                message="Ollama is not running or not accessible",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "provider": "ollama",
                    "endpoint": "http://localhost:11434",
                    "suggestion": "Start Ollama with: ollama serve"
                }
            )
    
    def check_configuration_validity(self, config: Dict[str, Any]) -> HealthCheck:
        """
        Check configuration validity.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            HealthCheck with configuration status
        """
        start_time = time.time()
        
        try:
            issues = []
            status = HealthStatus.HEALTHY
            
            # Check required configuration keys
            required_keys = ["llm_provider", "llm_model_name"]
            for key in required_keys:
                if key not in config or not config[key]:
                    issues.append(f"Missing required configuration: {key}")
                    status = HealthStatus.CRITICAL
            
            # Check LLM provider validity
            valid_providers = ["openai", "anthropic", "ollama"]
            if config.get("llm_provider") not in valid_providers:
                issues.append(f"Invalid LLM provider: {config.get('llm_provider')}")
                status = HealthStatus.CRITICAL
            
            # Check API keys for cloud providers
            provider = config.get("llm_provider")
            if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
                issues.append("OpenAI API key not found in environment")
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
            elif provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
                issues.append("Anthropic API key not found in environment")
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
            
            # Check temperature bounds
            temperature = config.get("llm_temperature", 0.7)
            if not isinstance(temperature, (int, float)) or not 0.0 <= temperature <= 2.0:
                issues.append(f"Invalid temperature value: {temperature} (should be 0.0-2.0)")
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
            
            message = "Configuration is valid" if not issues else "; ".join(issues)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="configuration_validity",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "config_keys": list(config.keys()),
                    "issues_found": len(issues),
                    "provider": config.get("llm_provider"),
                    "model": config.get("llm_model_name")
                }
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="configuration_validity",
                status=HealthStatus.CRITICAL,
                message=f"Configuration check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={"error": str(e)}
            )
    
    def check_agent_responsiveness(self, agent_test_func: Callable[[], Any]) -> HealthCheck:
        """
        Check agent responsiveness by running a simple test.
        
        Args:
            agent_test_func: Function that tests agent functionality
            
        Returns:
            HealthCheck with agent responsiveness status
        """
        start_time = time.time()
        
        try:
            # Run the agent test function with timeout
            result = agent_test_func()
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine status based on response time
            if duration_ms >= self._thresholds["response_time_critical"]:
                status = HealthStatus.CRITICAL
                message = f"Agent response time critical: {duration_ms:.0f}ms"
            elif duration_ms >= self._thresholds["response_time_warning"]:
                status = HealthStatus.WARNING
                message = f"Agent response time slow: {duration_ms:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Agent responsive: {duration_ms:.0f}ms"
            
            return HealthCheck(
                name="agent_responsiveness",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    "response_time_ms": duration_ms,
                    "test_result": str(result)[:200]  # Truncate long results
                }
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="agent_responsiveness",
                status=HealthStatus.CRITICAL,
                message=f"Agent test failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                details={"error": str(e)}
            )
    
    def run_all_health_checks(
        self, 
        config: Optional[Dict[str, Any]] = None,
        check_llm_providers: Optional[List[str]] = None,
        agent_test_func: Optional[Callable[[], Any]] = None
    ) -> Dict[str, HealthCheck]:
        """
        Run comprehensive health checks.
        
        Args:
            config: Configuration to validate
            check_llm_providers: List of LLM providers to check
            agent_test_func: Function to test agent responsiveness
            
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        # System resources check
        results["system_resources"] = self.check_system_resources()
        
        # Configuration check
        if config:
            results["configuration"] = self.check_configuration_validity(config)
        
        # LLM connectivity checks
        if check_llm_providers:
            for provider in check_llm_providers:
                api_key = None
                if provider == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                elif provider == "anthropic":
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                
                results[f"llm_{provider}"] = self.check_llm_connectivity(provider, api_key)
        
        # Agent responsiveness check
        if agent_test_func:
            results["agent_responsiveness"] = self.check_agent_responsiveness(agent_test_func)
        
        # Store results in history
        self._health_history.extend(results.values())
        self._last_check_time = datetime.utcnow()
        
        # Clean up old history (keep last 1000 checks)
        if len(self._health_history) > 1000:
            self._health_history = self._health_history[-1000:]
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status summary.
        
        Returns:
            System status with health indicators and recommendations
        """
        latest_checks = {}
        
        # Get the most recent check for each component
        for check in reversed(self._health_history):
            if check.name not in latest_checks:
                latest_checks[check.name] = check
        
        # Calculate overall health status
        overall_status = HealthStatus.HEALTHY
        critical_issues = []
        warning_issues = []
        
        for check in latest_checks.values():
            if check.status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                critical_issues.append(f"{check.name}: {check.message}")
            elif check.status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                warning_issues.append(f"{check.name}: {check.message}")
        
        # Generate recommendations
        recommendations = []
        if critical_issues:
            recommendations.append("Address critical issues immediately")
        if warning_issues:
            recommendations.append("Monitor warning conditions")
        if not critical_issues and not warning_issues:
            recommendations.append("System is operating normally")
        
        return {
            "overall_status": overall_status.value,
            "last_check_time": self._last_check_time.isoformat() if self._last_check_time else None,
            "total_checks_run": len(self._health_history),
            "components_status": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "last_checked": check.timestamp.isoformat(),
                    "response_time_ms": check.duration_ms
                }
                for name, check in latest_checks.items()
            },
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "recommendations": recommendations,
            "thresholds": self._thresholds
        }
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get health trends over specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Health trends and patterns
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_checks = [
            check for check in self._health_history
            if check.timestamp >= cutoff_time
        ]
        
        # Analyze trends by component
        trends = {}
        for check in recent_checks:
            if check.name not in trends:
                trends[check.name] = {
                    "checks_count": 0,
                    "healthy_count": 0,
                    "warning_count": 0,
                    "critical_count": 0,
                    "avg_response_time_ms": 0.0,
                    "total_response_time_ms": 0.0
                }
            
            trend = trends[check.name]
            trend["checks_count"] += 1
            trend["total_response_time_ms"] += check.duration_ms
            
            if check.status == HealthStatus.HEALTHY:
                trend["healthy_count"] += 1
            elif check.status == HealthStatus.WARNING:
                trend["warning_count"] += 1
            elif check.status == HealthStatus.CRITICAL:
                trend["critical_count"] += 1
        
        # Calculate averages and rates
        for trend in trends.values():
            if trend["checks_count"] > 0:
                trend["avg_response_time_ms"] = trend["total_response_time_ms"] / trend["checks_count"]
                trend["healthy_rate"] = trend["healthy_count"] / trend["checks_count"]
                trend["warning_rate"] = trend["warning_count"] / trend["checks_count"]
                trend["critical_rate"] = trend["critical_count"] / trend["checks_count"]
            del trend["total_response_time_ms"]  # Remove intermediate calculation
        
        return {
            "period_hours": hours,
            "total_checks": len(recent_checks),
            "component_trends": trends,
            "summary": {
                "most_reliable": max(trends.keys(), key=lambda k: trends[k]["healthy_rate"]) if trends else None,
                "least_reliable": min(trends.keys(), key=lambda k: trends[k]["healthy_rate"]) if trends else None,
                "fastest_component": min(trends.keys(), key=lambda k: trends[k]["avg_response_time_ms"]) if trends else None,
                "slowest_component": max(trends.keys(), key=lambda k: trends[k]["avg_response_time_ms"]) if trends else None
            }
        }

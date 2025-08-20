"""
Task data models and specifications for AICrewDev.

This module defines the data structures and specifications used for
task configuration, workflow definitions, and task management.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class TaskType(str, Enum):
    """Enumeration of available task types in the development workflow."""
    PLANNING = "planning"
    DESIGN = "design" 
    DEVELOPMENT = "development"
    TESTING = "testing"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    ANALYSIS = "analysis"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"

class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskSpecification(BaseModel):
    """
    Specification for creating a task with specific requirements and configuration.
    
    This model defines all the parameters needed to create and configure
    a task within the CrewAI framework.
    """
    
    # Basic Task Information
    task_type: TaskType = Field(description="Type of task to be executed")
    title: str = Field(description="Human-readable title for the task")
    description: str = Field(description="Detailed description of what the task should accomplish")
    
    # Task Requirements
    expected_output: str = Field(description="Expected format and content of task output")
    acceptance_criteria: List[str] = Field(
        default_factory=list, 
        description="List of criteria that must be met for task completion"
    )
    
    # Task Configuration
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    estimated_duration: Optional[int] = Field(
        default=None, 
        ge=1, 
        description="Estimated duration in minutes"
    )
    max_execution_time: Optional[int] = Field(
        default=None, 
        ge=30, 
        le=3600, 
        description="Maximum execution time in seconds"
    )
    
    # Dependencies and Context
    dependencies: List[str] = Field(
        default_factory=list, 
        description="List of task IDs that must be completed before this task"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional context and data for task execution"
    )
    
    # Output Configuration
    output_format: str = Field(default="text", description="Expected output format (text, json, markdown, etc.)")
    save_output: bool = Field(default=True, description="Whether to save task output")
    
    # Tools and Resources
    required_tools: List[str] = Field(
        default_factory=list, 
        description="List of tools required for task execution"
    )
    
    # Quality Assurance
    review_required: bool = Field(default=False, description="Whether task output requires review")
    auto_validation: bool = Field(default=True, description="Enable automatic output validation")
    
    # Custom Properties
    custom_properties: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Custom properties for specialized task configurations"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
    
    @classmethod
    def for_design_task(cls, **kwargs) -> "TaskSpecification":
        """
        Create a specification for a design/architecture task.
        
        Returns:
            TaskSpecification: Configured design task specification
        """
        defaults = {
            "task_type": TaskType.DESIGN,
            "title": "System Design and Architecture",
            "description": "Create comprehensive system design and architecture documentation",
            "expected_output": "Detailed architecture document with system design, component diagrams, and technical specifications",
            "acceptance_criteria": [
                "System architecture diagram is complete and clear",
                "All major components are documented",
                "Technology stack is specified",
                "Performance and scalability considerations are addressed",
                "Security requirements are included"
            ],
            "priority": TaskPriority.HIGH,
            "estimated_duration": 120,
            "output_format": "markdown",
            "required_tools": ["architecture_tools", "diagramming", "documentation"],
            "review_required": True
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_development_task(cls, feature_description: str, **kwargs) -> "TaskSpecification":
        """
        Create a specification for a development task.
        
        Args:
            feature_description: Description of the feature to develop
            
        Returns:
            TaskSpecification: Configured development task specification
        """
        defaults = {
            "task_type": TaskType.DEVELOPMENT,
            "title": f"Implement {feature_description}",
            "description": f"Develop and implement {feature_description} following best practices and design specifications",
            "expected_output": "Working code implementation with proper testing and documentation",
            "acceptance_criteria": [
                "Code follows established coding standards",
                "Unit tests are implemented with good coverage",
                "Code is properly documented",
                "Feature works as specified",
                "No security vulnerabilities introduced"
            ],
            "priority": TaskPriority.HIGH,
            "estimated_duration": 240,
            "output_format": "code",
            "required_tools": ["code_editor", "testing_framework", "debugger"],
            "review_required": True,
            "context": {"feature": feature_description}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_review_task(cls, review_subject: str, **kwargs) -> "TaskSpecification":
        """
        Create a specification for a code/design review task.
        
        Args:
            review_subject: What is being reviewed
            
        Returns:
            TaskSpecification: Configured review task specification
        """
        defaults = {
            "task_type": TaskType.REVIEW,
            "title": f"Review {review_subject}",
            "description": f"Perform comprehensive review of {review_subject} for quality, security, and best practices",
            "expected_output": "Detailed review report with findings, recommendations, and approval status",
            "acceptance_criteria": [
                "All code/design has been thoroughly reviewed",
                "Security considerations have been evaluated",
                "Best practices compliance has been checked",
                "Performance implications have been assessed",
                "Clear recommendations are provided"
            ],
            "priority": TaskPriority.MEDIUM,
            "estimated_duration": 90,
            "output_format": "markdown",
            "required_tools": ["static_analysis", "security_scanner", "code_metrics"],
            "review_required": False,  # Review tasks don't need further review
            "context": {"review_subject": review_subject}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_analysis_task(cls, analysis_target: str, **kwargs) -> "TaskSpecification":
        """
        Create a specification for an analysis task.
        
        Args:
            analysis_target: What is being analyzed
            
        Returns:
            TaskSpecification: Configured analysis task specification
        """
        defaults = {
            "task_type": TaskType.ANALYSIS,
            "title": f"Analyze {analysis_target}",
            "description": f"Perform detailed analysis of {analysis_target} to identify patterns, issues, and opportunities",
            "expected_output": "Comprehensive analysis report with findings, metrics, and actionable recommendations",
            "acceptance_criteria": [
                "Analysis is thorough and data-driven",
                "Key metrics and KPIs are identified",
                "Issues and opportunities are clearly documented",
                "Recommendations are actionable and prioritized",
                "Supporting data and evidence is provided"
            ],
            "priority": TaskPriority.MEDIUM,
            "estimated_duration": 150,
            "output_format": "json",
            "required_tools": ["analytics", "metrics_collection", "reporting"],
            "context": {"analysis_target": analysis_target}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_testing_task(cls, test_scope: str, **kwargs) -> "TaskSpecification":
        """
        Create a specification for a testing task.
        
        Args:
            test_scope: Scope of testing to be performed
            
        Returns:
            TaskSpecification: Configured testing task specification
        """
        defaults = {
            "task_type": TaskType.TESTING,
            "title": f"Test {test_scope}",
            "description": f"Create and execute comprehensive tests for {test_scope}",
            "expected_output": "Test suite with results, coverage report, and quality assessment",
            "acceptance_criteria": [
                "Test coverage meets minimum requirements (80%+)",
                "All critical paths are tested",
                "Edge cases and error conditions are covered",
                "Performance tests are included where applicable",
                "Test documentation is complete"
            ],
            "priority": TaskPriority.HIGH,
            "estimated_duration": 180,
            "output_format": "json",
            "required_tools": ["testing_framework", "coverage_tools", "performance_testing"],
            "context": {"test_scope": test_scope}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    def to_task_kwargs(self) -> Dict[str, Any]:
        """
        Convert specification to kwargs suitable for CrewAI Task creation.
        
        Returns:
            Dict[str, Any]: Task creation parameters
        """
        kwargs: Dict[str, Any] = {
            "description": self.description,
            "expected_output": self.expected_output,
        }
        
        # Add optional parameters if specified
        if self.max_execution_time:
            kwargs["max_execution_time"] = self.max_execution_time
        
        if self.context:
            kwargs["context"] = self.context
        
        return kwargs
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the task specification.
        
        Returns:
            Dict[str, Any]: Task summary
        """
        return {
            "title": self.title,
            "type": self.task_type,
            "priority": self.priority,
            "estimated_duration": self.estimated_duration,
            "dependencies_count": len(self.dependencies),
            "tools_required": len(self.required_tools),
            "review_required": self.review_required
        }

__all__ = ["TaskType", "TaskPriority", "TaskStatus", "TaskSpecification"]

"""
Performance monitoring utilities for tracking request times.
"""
import time
from functools import wraps
from typing import Callable


class PerformanceMonitor:
    """Simple performance monitoring for API endpoints."""
    
    def __init__(self):
        self.metrics = {}
    
    def track(self, name: str):
        """Decorator to track execution time of functions."""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - start
                    self._record(name, elapsed, success=True)
                    return result
                except Exception as e:
                    elapsed = time.time() - start
                    self._record(name, elapsed, success=False)
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start
                    self._record(name, elapsed, success=True)
                    return result
                except Exception as e:
                    elapsed = time.time() - start
                    self._record(name, elapsed, success=False)
                    raise
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    def _record(self, name: str, elapsed: float, success: bool):
        """Record a metric."""
        if name not in self.metrics:
            self.metrics[name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'failures': 0
            }
        
        metric = self.metrics[name]
        metric['count'] += 1
        metric['total_time'] += elapsed
        metric['min_time'] = min(metric['min_time'], elapsed)
        metric['max_time'] = max(metric['max_time'], elapsed)
        if not success:
            metric['failures'] += 1
    
    def get_stats(self, name: str = None):
        """Get statistics for a specific metric or all metrics."""
        if name:
            if name not in self.metrics:
                return None
            metric = self.metrics[name]
            return {
                'name': name,
                'avg_time': metric['total_time'] / metric['count'] if metric['count'] > 0 else 0,
                'min_time': metric['min_time'] if metric['min_time'] != float('inf') else 0,
                'max_time': metric['max_time'],
                'total_calls': metric['count'],
                'failure_rate': metric['failures'] / metric['count'] if metric['count'] > 0 else 0
            }
        
        # Return all metrics
        return {
            name: self.get_stats(name)
            for name in self.metrics.keys()
        }
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()


# Global monitor instance
monitor = PerformanceMonitor()

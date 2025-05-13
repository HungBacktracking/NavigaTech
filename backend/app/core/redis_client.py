import json
import pickle
import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
import redis
import hashlib
import inspect
from datetime import timedelta


T = TypeVar("T")


class RedisClient:
    def __init__(
        self, 
        host: str, 
        port: int, 
        password: str = None,
        db: int = 0,
        default_timeout: int = 3600,
    ):
        """
        Initialize Redis client
        
        Args:
            host: Redis host
            port: Redis port
            password: Redis password
            db: Redis database number
            default_timeout: Default cache timeout in seconds
        """
        self.redis = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=False,  # Don't decode responses, we'll handle serialization
            socket_timeout=5,  # Set socket timeout
            socket_connect_timeout=5,  # Set connection timeout
        )
        self.default_timeout = default_timeout
        
        # Initialize metrics tracking
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "pattern_deletes": {},  # Track by pattern prefix for targeted optimization
        }
        
    def ping(self) -> bool:
        """
        Check Redis connection
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            return self.redis.ping()
        except Exception:
            self._metrics["errors"] += 1
            return False
    
    def get(self, key: str) -> Any:
        """
        Get value from Redis
        
        Args:
            key: Cache key
            
        Returns:
            Any: Cached value or None if not found
        """
        try:
            data = self.redis.get(key)
            if data:
                self._metrics["hits"] += 1
                return pickle.loads(data)
            self._metrics["misses"] += 1
            return None
        except Exception:
            self._metrics["errors"] += 1
            return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """
        Set value in Redis
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds, defaults to default_timeout
            
        Returns:
            bool: True if successful, False otherwise
        """
        if timeout is None:
            timeout = self.default_timeout
            
        try:
            serialized = pickle.dumps(value)
            result = self.redis.setex(key, timeout, serialized)
            if result:
                self._metrics["sets"] += 1
            return result
        except Exception:
            self._metrics["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from Redis
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.redis.delete(key))
        except Exception:
            self._metrics["errors"] += 1
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all cache
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.redis.flushdb()
        except Exception:
            self._metrics["errors"] += 1
            return False
            
    def flush_by_pattern(self, pattern: str) -> int:
        """
        Clear cache by pattern
        
        Args:
            pattern: Key pattern to match
            
        Returns:
            int: Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                # Track pattern usage for optimization
                pattern_prefix = pattern.split(":")[0] if ":" in pattern else pattern
                if pattern_prefix not in self._metrics["pattern_deletes"]:
                    self._metrics["pattern_deletes"][pattern_prefix] = 0
                self._metrics["pattern_deletes"][pattern_prefix] += 1
                
                return self.redis.delete(*keys)
            return 0
        except Exception:
            self._metrics["errors"] += 1
            return 0
            
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics for monitoring
        
        Returns:
            Dict: Dictionary containing cache metrics
        """
        metrics = dict(self._metrics)
        
        # Calculate hit ratio
        total_gets = metrics["hits"] + metrics["misses"]
        metrics["hit_ratio"] = metrics["hits"] / total_gets if total_gets > 0 else 0
        
        # Add timestamp
        metrics["timestamp"] = datetime.datetime.now().isoformat()
        
        return metrics
        
    def reset_metrics(self) -> None:
        """
        Reset cache metrics
        """
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "pattern_deletes": {},
        }

    def cache_warmup(self, generator_func: Callable, key_pattern: str, timeout: int = None) -> int:
        """
        Warm up cache with generated data
        
        This method is useful for pre-populating cache after cache invalidation
        or during application startup for frequently accessed data.
        
        Args:
            generator_func: A function that generates (key, value) pairs to cache
            key_pattern: Only warm up keys matching this pattern (for selective warmup)
            timeout: Cache timeout in seconds, defaults to default_timeout
            
        Returns:
            int: Number of keys warmed up
        """
        try:
            count = 0
            for key, value in generator_func():
                # Only cache if the key matches the pattern
                if key.startswith(key_pattern):
                    self.set(key, value, timeout)
                    count += 1
            return count
        except Exception as e:
            print(f"Error during cache warmup: {str(e)}")
            return 0


def generate_cache_key(prefix: str, args: tuple, kwargs: Dict[str, Any]) -> str:
    """
    Generate a unique cache key based on function arguments
    
    Args:
        prefix: Key prefix
        args: Function positional arguments
        kwargs: Function keyword arguments
        
    Returns:
        str: Cache key
    """
    # Convert args and kwargs to something hashable
    key_parts = [prefix]
    
    # Add positional args
    for arg in args:
        if hasattr(arg, "__dict__"):
            # For objects, use their __dict__ representation
            key_parts.append(str(sorted(arg.__dict__.items())))
        else:
            key_parts.append(str(arg))
    
    # Add keyword args (sorted to ensure consistent order)
    sorted_kwargs = sorted(kwargs.items())
    for k, v in sorted_kwargs:
        if hasattr(v, "__dict__"):
            key_parts.append(f"{k}={sorted(v.__dict__.items())}")
        else:
            key_parts.append(f"{k}={v}")
    
    # Join parts and hash
    key_str = "_".join(key_parts)
    return f"{prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"


def redis_cache(
    timeout: int = None,
    key_prefix: str = None,
    redis_client: RedisClient = None,
):
    """
    Cache decorator for functions
    
    Args:
        timeout: Cache timeout in seconds (uses client default if None)
        key_prefix: Prefix for cache key (uses function name if None)
        redis_client: RedisClient instance (must be passed when the decorator is used)
        
    Returns:
        Function decorator
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not redis_client or not redis_client.ping():
                # If Redis is not available, just execute the function
                return func(*args, **kwargs)
            
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = generate_cache_key(prefix, args, kwargs)
            
            # Try to get from cache
            cached_value = redis_client.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    
    return decorator


def cache_invalidate(
    redis_client: RedisClient,
    key_prefix: str,
):
    """
    Invalidate cache for a specific prefix
    
    Args:
        redis_client: RedisClient instance
        key_prefix: Prefix for cache keys to invalidate
        
    Returns:
        int: Number of keys deleted
    """
    return redis_client.flush_by_pattern(f"{key_prefix}:*") 
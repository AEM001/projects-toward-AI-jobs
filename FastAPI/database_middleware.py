"""
Database query monitoring with slow query logging
"""
import logging
import time
from sqlalchemy import event
from db import engine
from config import settings

from log_config import get_slow_query_logger

# Create logger specifically for slow queries
slow_query_logger = get_slow_query_logger()
 
# Threshold for slow queries (in seconds)
SLOW_QUERY_THRESHOLD = settings.slow_query_threshold  # 100ms for SQLite, adjust for production

class QueryTimer:
    def __init__(self, threshold=0.1):
        self.threshold=threshold
        self.setup_event_listeners()

    def setup_event_listeners(self):
        """Set up SQLAlchemy event listeners to capture query timing"""
        @event.listens_for(engine,"before_cursor_execute")
        def before_cursor_execute(conn,cursor,statement,parameters,context,executemany):
            #store start time in the connection's info dict
            conn.info.setdefault("query_start_time",time.time())
            conn.info["query_sql"]=statement

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            # Calculate duration
            start_time = conn.info.get("query_start_time", time.time())
            duration = time.time() - start_time
            
            # Log all queries at DEBUG level (optional)
            logging.getLogger("sqlalchemy").debug(
                f"Query executed in {duration:.4f}s: {statement[:100]}..."
            )
            
            # Log slow queries at WARNING level
            if duration > self.threshold:
                slow_query_logger.warning(
                    f"SLOW QUERY DETECTED | "
                    f"Duration: {duration:.4f}s | "
                    f"SQL: {statement} | "
                    f"Parameters: {parameters}"
                )

# Initialize the query timer
query_timer = QueryTimer(threshold=SLOW_QUERY_THRESHOLD)
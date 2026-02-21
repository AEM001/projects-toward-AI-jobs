"""
Database query monitoring with slow query logging
"""
import logging
import time
import os
from datetime import datetime
from sqlalchemy import event
from db import engine
from config import settings

# Threshold for slow queries (in seconds)
SLOW_QUERY_THRESHOLD = settings.slow_query_threshold  # 100ms for SQLite, adjust for production

LOG_PATH = os.path.join(os.path.dirname(__file__), "app.log")

def _write_log(level: str, message: str):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {level} slow_query {message}\n"
    with open(LOG_PATH, "a") as f:
        f.write(line)
    print(line.strip())

class QueryTimer:
    def __init__(self, threshold=0.1):
        self.threshold=threshold
        self.setup_event_listeners()

    def setup_event_listeners(self):
        """Set up SQLAlchemy event listeners to capture query timing"""
        @event.listens_for(engine,"before_cursor_execute")
        def before_cursor_execute(conn,cursor,statement,parameters,context,executemany):
            #store start time in the connection's info dict (fresh for each query)
            conn.info["query_start_time"] = time.time()#should not use setdefault or it would use the time when the system starts
            conn.info["query_sql"] = statement

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            # Calculate duration
            start_time = conn.info.get("query_start_time", time.time())
            duration = time.time() - start_time
            
            # Log slow queries at WARNING level
            if duration > self.threshold:
                _write_log(
                    "WARNING",
                    f"SLOW QUERY DETECTED | Duration: {duration:.4f}s | SQL: {statement[:200]} | Parameters: {parameters}"
                )

# Initialize the query timer
query_timer = QueryTimer(threshold=SLOW_QUERY_THRESHOLD)
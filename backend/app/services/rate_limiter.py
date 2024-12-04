from datetime import datetime
import time
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        # store ip and usage timestamps
        self._usage: Dict[str, list] = {}
        
        # max num of complete cycles per day
        self.max_daily_cycles = 3
        
        # time windows in seconds (24 hours)
        self.time_window = 24 * 60 * 60
        
        # store active sessions to track completion
        self._active_sessions: Dict[str, Dict] = {}
        
    def _clean_old_requests(self, ip: str):
        """Remove requests older than 24 hours"""
        if ip in self._usage:
            current_time = time.time()
            self._usage[ip] = [
                timestamp for timestamp in self._usage[ip]
                if current_time - timestamp < self.time_window
            ]
            
    def start_cycle(self, ip: str) -> Tuple[bool, Dict]:
        """
        Start a new cycle if user hasn't exceeded their limit
        Returns: (is_allowed: bool, rate_limit_info: Dict)
        """
        self._clean_old_requests(ip)
        
        current_time = time.time()
        
        #initialize usage data for new IPs
        if ip not in self._usage:
            self._usage[ip] = []
            
        # get current usage count
        current_usage = len(self._usage[ip])
        
        # check if limit is exceeded
        if current_usage >= self.max_daily_cycles:
            oldest_request = self._usage[ip][0]
            reset_time = oldest_request + self.time_window
            time_remaining = reset_time - current_time
            
            return False, {
                "cycles_remaining": 0,
                "time_remaining_seconds": int(time_remaining),
                "total_daily_limit": self.max_daily_cycles,
                "active_cycle": False
            }
            
        # add new request timestamp
        self._usage[ip].append(current_time)
        
        # create active session
        session_id = f"{ip}_{current_time}"
        self._active_sessions[session_id] = {
            "ip": ip,
            "timestamp": current_time,
            "status": "active"
        }
        
        return True, {
            "cycles_remaining": self.max_daily_cycles - len(self._usage[ip]),
            "time_remaining_seconds": int(self.time_window),
            "total_daily_limit": self.max_daily_cycles,
            "active_cycle": True,
            "session_id": session_id
        }
        
    def check_status(self, ip: str) -> Dict:
        """Check current rate limit status without starting a new cycle"""
        self._clean_old_requests(ip)
        
        current_time = time.time()
        current_usage = len(self._usage.get(ip, []))
        
        # find if there's an active session
        active_session = None
        for session_id, session in self._active_sessions.items():
            if session["ip"] == ip and session["status"] == "active":
                active_session = session_id
                break
        
        if current_usage > self.max_daily_cycles:
            oldest_request = self._usage[ip][0]
            reset_time = oldest_request + self.time_window
            time_remaining = reset_time - current_time
        else:
            time_remaining = self.time_window
            
        return {
            "cycles_remaining": max(0, self.max_daily_cycles - current_usage),
            "time_remaining_seconds": int(time_remaining),
            "total_daily_limit": self.max_daily_cycles,
            "active_cycle": active_session is not None,
            "session_id": active_session
        }
        

rate_limiter = RateLimiter()
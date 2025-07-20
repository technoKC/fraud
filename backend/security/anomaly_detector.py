import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from typing import Dict, List, Tuple
import json

logger = logging.getLogger('anomaly_detection')

class AnomalyDetector:
    """AI-powered Anomaly Detection for security monitoring"""
    
    def __init__(self):
        self.request_history = defaultdict(list)
        self.login_patterns = defaultdict(list)
        self.transaction_patterns = defaultdict(list)
        self.anomaly_scores = {}
        
        # Thresholds
        self.request_rate_threshold = 100  # requests per minute
        self.unusual_time_threshold = 0.7  # confidence score
        self.location_change_threshold = 500  # km
        
        # ML model parameters (simplified for demonstration)
        self.baseline_patterns = {
            'normal_hours': list(range(8, 18)),  # 8 AM to 6 PM
            'normal_request_rate': 10,  # per minute
            'normal_transaction_amount': 50000,
            'normal_transaction_frequency': 5  # per hour
        }
    
    def analyze_login_pattern(self, username: str, ip: str, timestamp: datetime, 
                            location: Tuple[float, float] = None) -> Dict[str, any]:
        """Analyze login pattern for anomalies"""
        anomaly_score = 0
        anomalies = []
        
        # Time-based analysis
        hour = timestamp.hour
        if hour not in self.baseline_patterns['normal_hours']:
            anomaly_score += 0.3
            anomalies.append(f"Login at unusual hour: {hour}:00")
        
        # Geographic analysis
        if username in self.login_patterns and location:
            last_locations = [p['location'] for p in self.login_patterns[username][-5:] if p.get('location')]
            if last_locations:
                avg_lat = np.mean([loc[0] for loc in last_locations])
                avg_lon = np.mean([loc[1] for loc in last_locations])
                distance = self._calculate_distance((avg_lat, avg_lon), location)
                
                if distance > self.location_change_threshold:
                    anomaly_score += 0.4
                    anomalies.append(f"Login from unusual location: {distance:.0f}km away")
        
        # Frequency analysis
        recent_logins = [
            p for p in self.login_patterns[username]
            if (timestamp - p['timestamp']).seconds < 3600  # Last hour
        ]
        
        if len(recent_logins) > 5:
            anomaly_score += 0.3
            anomalies.append(f"High login frequency: {len(recent_logins)} in last hour")
        
        # Store pattern
        self.login_patterns[username].append({
            'timestamp': timestamp,
            'ip': ip,
            'location': location,
            'anomaly_score': anomaly_score
        })
        
        # Keep only last 100 entries
        if len(self.login_patterns[username]) > 100:
            self.login_patterns[username] = self.login_patterns[username][-100:]
        
        # Log if anomaly detected
        if anomaly_score > 0.5:
            logger.warning(f"Login anomaly detected for {username}: Score={anomaly_score:.2f}, Reasons={anomalies}")
        
        return {
            'anomaly_score': anomaly_score,
            'is_anomaly': anomaly_score > 0.5,
            'anomalies': anomalies,
            'risk_level': self._get_risk_level(anomaly_score)
        }
    
    def analyze_request_pattern(self, user: str, endpoint: str, ip: str, 
                              timestamp: datetime) -> Dict[str, any]:
        """Analyze API request patterns for anomalies"""
        anomaly_score = 0
        anomalies = []
        
        # Rate limiting analysis
        user_requests = self.request_history[user]
        recent_requests = [
            r for r in user_requests 
            if (timestamp - r['timestamp']).seconds < 60
        ]
        
        request_rate = len(recent_requests)
        if request_rate > self.request_rate_threshold:
            anomaly_score += 0.5
            anomalies.append(f"High request rate: {request_rate}/min")
        
        # Endpoint pattern analysis
        endpoint_frequencies = defaultdict(int)
        for req in user_requests[-100:]:
            endpoint_frequencies[req['endpoint']] += 1
        
        # Check for unusual endpoint access
        sensitive_endpoints = ['/admin/', '/export/', '/delete/']
        if any(sensitive in endpoint for sensitive in sensitive_endpoints):
            anomaly_score += 0.2
            anomalies.append(f"Access to sensitive endpoint: {endpoint}")
        
        # Store request
        self.request_history[user].append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'ip': ip
        })
        
        # Keep only last 1000 entries
        if len(self.request_history[user]) > 1000:
            self.request_history[user] = self.request_history[user][-1000:]
        
        return {
            'anomaly_score': anomaly_score,
            'is_anomaly': anomaly_score > 0.5,
            'anomalies': anomalies,
            'risk_level': self._get_risk_level(anomaly_score)
        }
    
    def analyze_transaction_pattern(self, user: str, amount: float, 
                                  transaction_type: str, timestamp: datetime) -> Dict[str, any]:
        """Analyze transaction patterns for fraud detection"""
        anomaly_score = 0
        anomalies = []
        
        # Amount analysis
        if amount > self.baseline_patterns['normal_transaction_amount'] * 10:
            anomaly_score += 0.4
            anomalies.append(f"Unusually high amount: ₹{amount:,.0f}")
        
        # Frequency analysis
        recent_transactions = [
            t for t in self.transaction_patterns[user]
            if (timestamp - t['timestamp']).seconds < 3600
        ]
        
        if len(recent_transactions) > self.baseline_patterns['normal_transaction_frequency']:
            anomaly_score += 0.3
            anomalies.append(f"High transaction frequency: {len(recent_transactions)}/hour")
        
        # Velocity analysis
        if recent_transactions:
            total_recent_amount = sum(t['amount'] for t in recent_transactions)
            if total_recent_amount > self.baseline_patterns['normal_transaction_amount'] * 20:
                anomaly_score += 0.3
                anomalies.append(f"High velocity: ₹{total_recent_amount:,.0f} in last hour")
        
        # Store transaction
        self.transaction_patterns[user].append({
            'timestamp': timestamp,
            'amount': amount,
            'type': transaction_type,
            'anomaly_score': anomaly_score
        })
        
        return {
            'anomaly_score': anomaly_score,
            'is_anomaly': anomaly_score > 0.5,
            'anomalies': anomalies,
            'risk_level': self._get_risk_level(anomaly_score)
        }
    
    def get_security_dashboard_data(self) -> Dict[str, any]:
        """Get aggregated security data for dashboard"""
        total_anomalies = sum(
            1 for user_patterns in self.login_patterns.values()
            for pattern in user_patterns
            if pattern.get('anomaly_score', 0) > 0.5
        )
        
        high_risk_users = []
        for user, patterns in self.login_patterns.items():
            avg_score = np.mean([p.get('anomaly_score', 0) for p in patterns[-10:]])
            if avg_score > 0.5:
                high_risk_users.append({'user': user, 'risk_score': avg_score})
        
        return {
            'total_anomalies_detected': total_anomalies,
            'high_risk_users': sorted(high_risk_users, key=lambda x: x['risk_score'], reverse=True)[:5],
            'anomaly_trend': self._calculate_anomaly_trend(),
            'security_score': 100 - min(total_anomalies, 100)  # Simple security score
        }
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations in km (simplified)"""
        # Haversine formula (simplified)
        lat_diff = abs(loc1[0] - loc2[0])
        lon_diff = abs(loc1[1] - loc2[1])
        return np.sqrt(lat_diff**2 + lon_diff**2) * 111  # Rough conversion to km
    
    def _get_risk_level(self, score: float) -> str:
        """Convert anomaly score to risk level"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        return "NORMAL"
    
    def _calculate_anomaly_trend(self) -> List[Dict[str, any]]:
        """Calculate anomaly trend for last 24 hours"""
        now = datetime.now()
        trend = []
        
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            anomalies_in_hour = sum(
                1 for user_patterns in self.login_patterns.values()
                for pattern in user_patterns
                if hour_start <= pattern['timestamp'] < hour_end and pattern.get('anomaly_score', 0) > 0.5
            )
            
            trend.append({
                'hour': hour_start.strftime('%H:00'),
                'anomalies': anomalies_in_hour
            })
        
        return trend[::-1]  # Reverse to show oldest first
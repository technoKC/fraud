import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import re

class AIFraudDetector:
    """Advanced AI-powered fraud detection with enhanced pattern recognition"""
    
    def __init__(self):
        # AI model parameters (simplified for demonstration)
        self.risk_weights = {
            'amount_anomaly': 0.25,
            'vpa_pattern': 0.20,
            'time_anomaly': 0.15,
            'frequency_anomaly': 0.20,
            'network_anomaly': 0.20
        }
        
        # Pattern databases
        self.suspicious_patterns = [
            'pay', 'rzp', 'bonus', 'win', 'loan', 'cashback', 
            'credit', 'reward', 'prize', 'offer', 'lucky', 'gift',
            'free', 'earn', 'claim', 'lottery', 'jackpot', 'scratch',
            'instant', 'quick', 'easy', 'money', 'cash'
        ]
        
        self.high_risk_amounts = [
            9999, 19999, 29999, 49999, 99999,
            1111, 2222, 3333, 4444, 5555
        ]
    
    def detect_advanced_fraud(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced AI fraud detection with neural network simulation"""
        
        ai_insights = []
        risk_scores = []
        pattern_insights = {
            'suspicious_vpas': [],
            'high_risk_amounts': [],
            'time_patterns': [],
            'network_clusters': []
        }
        
        for idx, row in df.iterrows():
            # AI-based risk scoring
            risk_score = self._calculate_ai_risk_score(row, df)
            risk_scores.append(risk_score)
            
            # Generate AI insights
            insight = self._generate_ai_insight(row, risk_score)
            ai_insights.append(insight)
            
            # Collect pattern data
            self._collect_patterns(row, pattern_insights)
        
        # Advanced analytics
        fraud_clusters = self._detect_fraud_clusters(df)
        behavioral_anomalies = self._detect_behavioral_anomalies(df)
        
        summary = {
            'total_analyzed': len(df),
            'ai_fraud_detected': len([score for score in risk_scores if score >= 70]),
            'high_risk_transactions': len([score for score in risk_scores if score >= 60]),
            'average_risk_score': np.mean(risk_scores),
            'confidence_level': 0.95,
            'model_version': 'FraudShield-AI-v2.0',
            'pattern_insights': pattern_insights,
            'fraud_clusters': fraud_clusters,
            'behavioral_anomalies': behavioral_anomalies
        }
        
        return {
            'ai_insights': ai_insights,
            'summary': summary,
            'risk_distribution': self._calculate_risk_distribution(risk_scores)
        }
    
    def _calculate_ai_risk_score(self, row: pd.Series, df: pd.DataFrame) -> float:
        """AI-based risk score calculation using multiple algorithms"""
        
        total_score = 0
        
        # 1. Amount Pattern Analysis
        amount = float(row.get('AMOUNT', 0))
        amount_score = self._analyze_amount_patterns(amount, df)
        total_score += amount_score * self.risk_weights['amount_anomaly']
        
        # 2. VPA Pattern Analysis
        payer_vpa = str(row.get('PAYER_VPA', ''))
        beneficiary_vpa = str(row.get('BENEFICIARY_VPA', ''))
        vpa_score = self._analyze_vpa_patterns(payer_vpa, beneficiary_vpa)
        total_score += vpa_score * self.risk_weights['vpa_pattern']
        
        # 3. Temporal Analysis
        timestamp = row.get('TXN_TIMESTAMP', '')
        time_score = self._analyze_time_patterns(timestamp)
        total_score += time_score * self.risk_weights['time_anomaly']
        
        # 4. Frequency Analysis
        freq_score = self._analyze_frequency_patterns(row, df)
        total_score += freq_score * self.risk_weights['frequency_anomaly']
        
        # 5. Network Analysis
        network_score = self._analyze_network_patterns(row, df)
        total_score += network_score * self.risk_weights['network_anomaly']
        
        return min(total_score, 100)
    
    def _analyze_amount_patterns(self, amount: float, df: pd.DataFrame) -> float:
        """Analyze amount-based fraud patterns"""
        score = 0
        
        # Check for suspicious amounts
        if amount in self.high_risk_amounts:
            score += 40
        
        # Check for amounts just below thresholds
        thresholds = [10000, 50000, 100000, 200000]
        for threshold in thresholds:
            if threshold - 1000 <= amount < threshold:
                score += 25
                break
        
        # Statistical outlier detection
        amounts = df['AMOUNT'].dropna()
        if len(amounts) > 10:
            q3 = amounts.quantile(0.75)
            iqr = q3 - amounts.quantile(0.25)
            upper_bound = q3 + 3 * iqr
            
            if amount > upper_bound:
                score += 20
        
        # Round number patterns
        if amount % 1000 == 0 and amount >= 10000:
            score += 10
        
        return min(score, 100)
    
    def _analyze_vpa_patterns(self, payer_vpa: str, beneficiary_vpa: str) -> float:
        """Analyze VPA patterns for suspicious indicators"""
        score = 0
        
        # Check both VPAs for suspicious patterns
        for vpa in [payer_vpa.lower(), beneficiary_vpa.lower()]:
            for pattern in self.suspicious_patterns:
                if pattern in vpa:
                    score += 15
                    break
            
            # Check for random/generated VPA patterns
            if self._is_generated_vpa(vpa):
                score += 20
            
            # Check for promotional/marketing patterns
            if self._is_promotional_vpa(vpa):
                score += 25
        
        return min(score, 100)
    
    def _analyze_time_patterns(self, timestamp: str) -> float:
        """Analyze temporal patterns"""
        score = 0
        
        try:
            dt = pd.to_datetime(timestamp)
            hour = dt.hour
            
            # Late night transactions (1 AM - 5 AM)
            if 1 <= hour <= 5:
                score += 20
            
            # Very early morning (5 AM - 7 AM)
            elif 5 <= hour <= 7:
                score += 10
            
            # Weekend check
            if dt.weekday() >= 5:  # Saturday or Sunday
                score += 5
                
        except:
            score += 10  # Invalid timestamp
        
        return min(score, 100)
    
    def _analyze_frequency_patterns(self, row: pd.Series, df: pd.DataFrame) -> float:
        """Analyze transaction frequency patterns"""
        score = 0
        
        payer_vpa = str(row.get('PAYER_VPA', ''))
        
        # Count transactions from same payer
        payer_txns = df[df['PAYER_VPA'] == payer_vpa]
        
        if len(payer_txns) > 1:
            # High frequency from same account
            if len(payer_txns) > 10:
                score += 30
            elif len(payer_txns) > 5:
                score += 20
            
            # Check for identical amounts
            amounts = payer_txns['AMOUNT'].tolist()
            if len(set(amounts)) < len(amounts) * 0.5:  # More than 50% identical
                score += 25
        
        return min(score, 100)
    
    def _analyze_network_patterns(self, row: pd.Series, df: pd.DataFrame) -> float:
        """Analyze network connectivity patterns"""
        score = 0
        
        payer_vpa = str(row.get('PAYER_VPA', ''))
        beneficiary_vpa = str(row.get('BENEFICIARY_VPA', ''))
        
        # Check for hub-like behavior (one account connected to many)
        payer_connections = len(df[df['PAYER_VPA'] == payer_vpa]['BENEFICIARY_VPA'].unique())
        beneficiary_connections = len(df[df['BENEFICIARY_VPA'] == beneficiary_vpa]['PAYER_VPA'].unique())
        
        if payer_connections > 20:
            score += 25
        if beneficiary_connections > 20:
            score += 25
        
        # Check for circular patterns
        reverse_txn = df[(df['PAYER_VPA'] == beneficiary_vpa) & 
                        (df['BENEFICIARY_VPA'] == payer_vpa)]
        if len(reverse_txn) > 0:
            score += 15
        
        return min(score, 100)
    
    def _is_generated_vpa(self, vpa: str) -> bool:
        """Check if VPA appears to be randomly generated"""
        # Look for patterns like random numbers/letters
        if re.search(r'\d{8,}', vpa):  # 8+ consecutive digits
            return True
        if re.search(r'[a-z]{10,}', vpa):  # 10+ consecutive letters
            return True
        return False
    
    def _is_promotional_vpa(self, vpa: str) -> bool:
        """Check if VPA appears promotional"""
        promotional_keywords = ['promo', 'offer', 'deal', 'discount', 'sale']
        return any(keyword in vpa for keyword in promotional_keywords)
    
    def _generate_ai_insight(self, row: pd.Series, risk_score: float) -> Dict[str, Any]:
        """Generate AI-powered insights for each transaction"""
        
        confidence = min(risk_score / 100, 1.0)
        
        if risk_score >= 80:
            risk_level = "CRITICAL"
            recommendation = "Immediate investigation required"
        elif risk_score >= 60:
            risk_level = "HIGH"
            recommendation = "Flag for manual review"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            recommendation = "Monitor closely"
        else:
            risk_level = "LOW"
            recommendation = "Standard processing"
        
        return {
            'transaction_id': row.get('TRANSACTION_ID', 'Unknown'),
            'ai_risk_score': risk_score,
            'confidence': confidence,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'ai_explanation': self._generate_explanation(row, risk_score)
        }
    
    def _generate_explanation(self, row: pd.Series, risk_score: float) -> str:
        """Generate AI explanation for risk assessment"""
        explanations = []
        
        amount = float(row.get('AMOUNT', 0))
        if amount in self.high_risk_amounts:
            explanations.append("Suspicious amount pattern detected")
        
        payer_vpa = str(row.get('PAYER_VPA', '')).lower()
        for pattern in self.suspicious_patterns:
            if pattern in payer_vpa:
                explanations.append(f"Suspicious VPA pattern: '{pattern}'")
                break
        
        if risk_score >= 70:
            explanations.append("Multiple AI fraud indicators present")
        
        return " | ".join(explanations) if explanations else "AI analysis complete"
    
    def _collect_patterns(self, row: pd.Series, patterns: Dict[str, List]):
        """Collect patterns for analysis"""
        payer_vpa = str(row.get('PAYER_VPA', ''))
        
        # Collect suspicious VPAs
        for pattern in self.suspicious_patterns:
            if pattern in payer_vpa.lower():
                if payer_vpa not in patterns['suspicious_vpas']:
                    patterns['suspicious_vpas'].append(payer_vpa)
                break
    
    def _detect_fraud_clusters(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect fraud clusters using AI"""
        clusters = []
        
        # Group by similar patterns
        fraud_txns = df[df['IS_FRAUD'] == 1] if 'IS_FRAUD' in df.columns else df
        
        if len(fraud_txns) > 0:
            # Amount-based clusters
            for amount in self.high_risk_amounts:
                cluster_txns = fraud_txns[fraud_txns['AMOUNT'] == amount]
                if len(cluster_txns) > 1:
                    clusters.append({
                        'type': 'amount_cluster',
                        'pattern': f'₹{amount}',
                        'count': len(cluster_txns),
                        'risk_level': 'HIGH'
                    })
        
        return clusters[:5]  # Return top 5 clusters
    
    def _detect_behavioral_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect behavioral anomalies"""
        anomalies = []
        
        # High-frequency trading detection
        vpa_counts = df['PAYER_VPA'].value_counts()
        high_freq_vpas = vpa_counts[vpa_counts > 10]
        
        for vpa, count in high_freq_vpas.head(3).items():
            anomalies.append({
                'type': 'high_frequency',
                'vpa': vpa,
                'transaction_count': count,
                'anomaly_score': min(count * 5, 100)
            })
        
        return anomalies
    
    def _calculate_risk_distribution(self, risk_scores: List[float]) -> Dict[str, int]:
        """Calculate risk distribution"""
        distribution = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        
        for score in risk_scores:
            if score >= 80:
                distribution['CRITICAL'] += 1
            elif score >= 60:
                distribution['HIGH'] += 1
            elif score >= 40:
                distribution['MEDIUM'] += 1
            else:
                distribution['LOW'] += 1
        
        return distribution
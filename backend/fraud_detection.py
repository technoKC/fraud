import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import re

class FraudDetector:
    def __init__(self):
        # Enhanced fraud indicators with AI integration
        self.fraud_vpa_patterns = [
            'pay', 'rzp', 'bonus', 'win', 'loan', 'cashback', 
            'credit', 'reward', 'prize', 'offer', 'lucky', 'gift',
            'free', 'earn', 'claim', 'lottery', 'jackpot'
        ]
        
        # Suspicious behavior patterns
        self.behavior_patterns = {
            'rapid_transactions': 5,  # More than 5 transactions in 10 minutes
            'round_amounts': [1000, 2000, 5000, 10000, 50000, 100000],
            'suspicious_times': list(range(1, 6)),  # 1 AM to 5 AM
            'high_risk_amounts': [9999, 19999, 29999, 49999, 99999]
        }
    
    def detect_fraud(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced fraud detection with AI-ready features"""
        results = {
            "fraud_count": 0,
            "fraud_transactions": [],
            "detailed_results": [],
            "pattern_summary": {},
            "risk_distribution": {}
        }
        
        # Initialize risk counters
        risk_levels = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        
        for idx, row in df.iterrows():
            # Base fraud check from IS_FRAUD column
            is_fraud = bool(row.get('IS_FRAUD', 0))
            
            # Enhanced pattern checking
            risk_factors = []
            risk_score = 0
            
            # 1. VPA Pattern Analysis - FIXED: Handle float values
            payer_vpa = self._safe_str(row.get('PAYER_VPA', ''))
            beneficiary_vpa = self._safe_str(row.get('BENEFICIARY_VPA', ''))
            
            suspicious_patterns = []
            for pattern in self.fraud_vpa_patterns:
                if pattern in payer_vpa.lower() or pattern in beneficiary_vpa.lower():
                    suspicious_patterns.append(pattern)
                    risk_score += 15
                    risk_factors.append(f"Suspicious pattern '{pattern}' in VPA")
            
            # 2. Amount Analysis
            amount = float(row.get('AMOUNT', 0))
            
            # Check for suspicious amounts
            if amount in self.behavior_patterns['high_risk_amounts']:
                risk_score += 20
                risk_factors.append(f"High-risk amount: ₹{amount:,.0f}")
            elif amount in self.behavior_patterns['round_amounts']:
                risk_score += 10
                risk_factors.append(f"Round amount: ₹{amount:,.0f}")
            
            # Check for amounts just below thresholds
            for threshold in [10000, 50000, 100000]:
                if threshold - 1000 <= amount < threshold:
                    risk_score += 15
                    risk_factors.append(f"Amount just below threshold: ₹{amount:,.0f}")
                    break
            
            # 3. Time-based Analysis - FIXED: Handle string conversion
            try:
                timestamp_str = self._safe_str(row.get('TXN_TIMESTAMP', ''))
                if timestamp_str:
                    timestamp = pd.to_datetime(timestamp_str)
                    hour = timestamp.hour
                    
                    if hour in self.behavior_patterns['suspicious_times']:
                        risk_score += 10
                        risk_factors.append(f"Suspicious time: {hour}:00 hrs")
                    
                    # Weekend check
                    if timestamp.weekday() >= 5:  # Saturday or Sunday
                        risk_score += 5
                        risk_factors.append("Weekend transaction")
            except:
                pass
            
            # 4. Device and Location Analysis - FIXED: Handle float values
            device_id = self._safe_str(row.get('DEVICE_ID', ''))
            ip_address = self._safe_str(row.get('IP_ADDRESS', ''))
            
            if not device_id or device_id == 'nan':
                risk_score += 10
                risk_factors.append("Missing device ID")
            
            if ip_address and (ip_address.startswith('10.') or ip_address == '0.0.0.0'):
                risk_score += 5
                risk_factors.append("Suspicious IP address")
            
            # 5. Transaction Status Check - FIXED: Handle string conversion
            trn_status = self._safe_str(row.get('TRN_STATUS', ''))
            response_code = self._safe_str(row.get('RESPONSE_CODE', ''))
            
            if trn_status != 'SUCCESS' or response_code != '00':
                risk_score += 5
                risk_factors.append("Transaction failure indicators")
            
            # Override risk score if marked as fraud
            if is_fraud:
                risk_score = max(risk_score, 80)
                risk_factors.insert(0, "Confirmed fraud in historical data")
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "Critical"
            elif risk_score >= 60:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            risk_levels[risk_level] += 1
            
            # Generate explanation
            explanation = self._generate_detailed_explanation(
                is_fraud, suspicious_patterns, risk_factors, risk_score
            )
            
            transaction_result = {
                "transaction_id": self._safe_str(row.get('TRANSACTION_ID', f'TXN_{idx}')),
                "timestamp": self._safe_str(row.get('TXN_TIMESTAMP', '')),
                "amount": amount,
                "payer_vpa": payer_vpa,
                "beneficiary_vpa": beneficiary_vpa,
                "is_fraud": is_fraud,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "suspicious_patterns": suspicious_patterns,
                "risk_factors": risk_factors,
                "explanation": explanation,
                "device_id": device_id,
                "ip_address": ip_address,
                "response_code": response_code
            }
            
            results["detailed_results"].append({
                "transaction": transaction_result,
                "classification": {
                    "label": "Fraud" if is_fraud or risk_score >= 60 else "Legitimate",
                    "confidence": min(risk_score / 100, 1.0),
                    "risk": risk_level
                },
                "explanation": [explanation],
                "recommendations": self._generate_recommendations(risk_level, risk_factors)
            })
            
            if is_fraud or risk_score >= 60:
                results["fraud_count"] += 1
                results["fraud_transactions"].append(transaction_result)
        
        # Generate pattern summary
        results["pattern_summary"] = self._generate_pattern_summary(df, results["fraud_transactions"])
        results["risk_distribution"] = risk_levels
        
        return results
    
    def _safe_str(self, value):
        """Safely convert any value to string, handling NaN and None"""
        if pd.isna(value) or value is None:
            return ""
        return str(value)
    
    def _generate_detailed_explanation(self, is_fraud: bool, patterns: List[str], 
                                     risk_factors: List[str], risk_score: float) -> str:
        """Generate detailed explanation for fraud detection"""
        explanations = []
        
        if is_fraud:
            explanations.append("⚠️ CONFIRMED FRAUD: Transaction flagged in historical fraud database")
        
        if risk_score >= 80:
            explanations.append("🚨 CRITICAL RISK: Multiple high-risk indicators detected")
        elif risk_score >= 60:
            explanations.append("⚠️ HIGH RISK: Significant suspicious patterns identified")
        elif risk_score >= 40:
            explanations.append("⚡ MEDIUM RISK: Some suspicious indicators present")
        
        if patterns:
            explanations.append(f"Suspicious VPA patterns: {', '.join(set(patterns))}")
        
        # Add top 3 risk factors
        if risk_factors:
            top_factors = risk_factors[:3]
            explanations.append(f"Key risk factors: {'; '.join(top_factors)}")
        
        if not explanations:
            explanations.append("✅ Transaction appears legitimate based on all checks")
        
        return " | ".join(explanations)
    
    def _generate_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate actionable recommendations based on risk analysis"""
        recommendations = []
        
        if risk_level == "Critical":
            recommendations.extend([
                "Immediate account freeze recommended",
                "Contact account holder for verification",
                "Review all recent transactions from this account"
            ])
        elif risk_level == "High":
            recommendations.extend([
                "Flag account for enhanced monitoring",
                "Require additional authentication for future transactions",
                "Review transaction history for patterns"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Monitor account for unusual activity",
                "Consider sending security alert to account holder"
            ])
        else:
            recommendations.append("Continue standard monitoring procedures")
        
        # Specific recommendations based on risk factors
        if any("device" in factor.lower() for factor in risk_factors):
            recommendations.append("Verify device authentication")
        
        if any("time" in factor.lower() for factor in risk_factors):
            recommendations.append("Check for automated/bot activity")
        
        if any("amount" in factor.lower() for factor in risk_factors):
            recommendations.append("Verify transaction purpose with account holder")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _generate_pattern_summary(self, df: pd.DataFrame, fraud_transactions: List[Dict]) -> Dict[str, Any]:
        """Generate summary of fraud patterns detected"""
        summary = {
            "total_analyzed": len(df),
            "fraud_detected": len(fraud_transactions),
            "fraud_rate": (len(fraud_transactions) / len(df) * 100) if len(df) > 0 else 0,
            "common_patterns": {},
            "peak_fraud_hours": [],
            "high_risk_vpas": [],
            "amount_analysis": {}
        }
        
        if fraud_transactions:
            # Analyze common patterns
            all_patterns = []
            for txn in fraud_transactions:
                all_patterns.extend(txn.get('suspicious_patterns', []))
            
            if all_patterns:
                from collections import Counter
                pattern_counts = Counter(all_patterns)
                summary["common_patterns"] = dict(pattern_counts.most_common(5))
            
            # Analyze fraud amounts
            fraud_amounts = [txn['amount'] for txn in fraud_transactions]
            summary["amount_analysis"] = {
                "average_fraud_amount": np.mean(fraud_amounts),
                "max_fraud_amount": max(fraud_amounts),
                "min_fraud_amount": min(fraud_amounts),
                "total_fraud_value": sum(fraud_amounts)
            }
            
            # Find high-risk VPAs
            fraud_vpas = []
            for txn in fraud_transactions:
                fraud_vpas.extend([txn['payer_vpa'], txn['beneficiary_vpa']])
            
            from collections import Counter
            vpa_counts = Counter(fraud_vpas)
            summary["high_risk_vpas"] = [vpa for vpa, count in vpa_counts.most_common(5) if count > 1]
        
        return summary
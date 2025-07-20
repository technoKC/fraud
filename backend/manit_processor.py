import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class ManitProcessor:
    def __init__(self):
        self.valid_departments = [
            'Computer Science', 'Electronics', 'Mechanical', 
            'Civil', 'Electrical', 'Chemical', 'Architecture'
        ]
        
        self.semester_fees = {
            'I': 45000, 'II': 45000, 'III': 50000, 'IV': 50000,
            'V': 55000, 'VI': 55000, 'VII': 60000, 'VIII': 60000
        }
    
    def process_loan_transactions(self, df: pd.DataFrame, status_dict: Dict[str, str]) -> Dict[str, Any]:
        """Process MANIT loan transactions for verification"""
        
        # Initialize counters
        received_count = 0
        verified_count = 0
        pending_count = 0
        rejected_count = 0
        
        # Process transactions
        processed_transactions = []
        
        for idx, row in df.iterrows():
            transaction_id = row.get('TRANSACTION_ID', f'LTX_{idx}')
            
            # Check if status has been manually updated
            if transaction_id in status_dict:
                status = status_dict[transaction_id]
            else:
                # Default status from CSV or auto-verify
                status = row.get('STATUS', 'Pending')
                
                # Auto-verification logic
                if status == 'Received':
                    # Verify against expected semester fees
                    semester = row.get('SEMESTER', '')
                    amount = float(row.get('LOAN_AMOUNT', 0))
                    expected_fee = self.semester_fees.get(semester, 0)
                    
                    if expected_fee > 0 and abs(amount - expected_fee) <= 5000:
                        status = 'verified'
                    else:
                        status = 'pending'
            
            # Create processed transaction
            processed_txn = {
                'transaction_id': transaction_id,
                'student_id': row.get('STUDENT_ID', ''),
                'student_name': row.get('STUDENT_NAME', ''),
                'amount': float(row.get('LOAN_AMOUNT', 0)),
                'semester': row.get('SEMESTER', ''),
                'department': row.get('DEPARTMENT', ''),
                'transaction_date': row.get('TRANSACTION_DATE', ''),
                'bank_name': row.get('BANK_NAME', ''),
                'status': status,
                'verification_notes': self._generate_verification_notes(row, status)
            }
            
            processed_transactions.append(processed_txn)
            
            # Update counters
            if status.lower() == 'received':
                received_count += 1
            elif status.lower() == 'verified':
                verified_count += 1
                received_count += 1  # Verified implies received
            elif status.lower() == 'pending':
                pending_count += 1
            elif status.lower() == 'rejected':
                rejected_count += 1
        
        # Calculate statistics
        total_amount_received = sum(t['amount'] for t in processed_transactions 
                                  if t['status'].lower() in ['received', 'verified'])
        total_amount_pending = sum(t['amount'] for t in processed_transactions 
                                 if t['status'].lower() == 'pending')
        
        # Department-wise statistics
        dept_stats = {}
        for dept in self.valid_departments:
            dept_txns = [t for t in processed_transactions if t['department'] == dept]
            dept_stats[dept] = {
                'total': len(dept_txns),
                'verified': len([t for t in dept_txns if t['status'].lower() == 'verified']),
                'pending': len([t for t in dept_txns if t['status'].lower() == 'pending']),
                'amount': sum(t['amount'] for t in dept_txns)
            }
        
        # Semester-wise statistics
        semester_stats = {}
        for sem in self.semester_fees.keys():
            sem_txns = [t for t in processed_transactions if t['semester'] == sem]
            semester_stats[sem] = {
                'total': len(sem_txns),
                'verified': len([t for t in sem_txns if t['status'].lower() == 'verified']),
                'expected_fee': self.semester_fees[sem],
                'total_amount': sum(t['amount'] for t in sem_txns)
            }
        
        return {
            'total_transactions': len(df),
            'received': received_count,
            'verified': verified_count,
            'pending': pending_count,
            'rejected': rejected_count,
            'total_amount_received': total_amount_received,
            'total_amount_pending': total_amount_pending,
            'transactions': processed_transactions,
            'department_statistics': dept_stats,
            'semester_statistics': semester_stats,
            'verification_rate': (verified_count / len(df) * 100) if len(df) > 0 else 0
        }
    
    def _generate_verification_notes(self, row: pd.Series, status: str) -> str:
        """Generate verification notes for a transaction"""
        notes = []
        
        # Check department validity
        dept = row.get('DEPARTMENT', '')
        if dept not in self.valid_departments:
            notes.append(f"Invalid department: {dept}")
        
        # Check amount against semester fees
        semester = row.get('SEMESTER', '')
        amount = float(row.get('LOAN_AMOUNT', 0))
        expected_fee = self.semester_fees.get(semester, 0)
        
        if expected_fee > 0:
            difference = amount - expected_fee
            if abs(difference) > 5000:
                notes.append(f"Amount mismatch: Expected ₹{expected_fee:,}, Received ₹{amount:,}")
            elif abs(difference) > 0:
                notes.append(f"Minor difference: ₹{abs(difference):,}")
        
        # Check transaction date
        try:
            txn_date = pd.to_datetime(row.get('TRANSACTION_DATE', ''))
            days_old = (datetime.now() - txn_date).days
            if days_old > 30:
                notes.append(f"Old transaction: {days_old} days")
        except:
            notes.append("Invalid transaction date")
        
        # Status-specific notes
        if status.lower() == 'verified':
            notes.append("✓ Auto-verified: All checks passed")
        elif status.lower() == 'pending':
            if not notes:
                notes.append("Manual verification required")
        elif status.lower() == 'rejected':
            notes.append("⚠ Transaction rejected")
        
        return " | ".join(notes) if notes else "Transaction appears valid"
    
    def validate_csv_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate MANIT CSV format"""
        required_columns = [
            'STUDENT_ID', 'STUDENT_NAME', 'TRANSACTION_ID', 
            'LOAN_AMOUNT', 'SEMESTER', 'DEPARTMENT', 
            'TRANSACTION_DATE', 'BANK_NAME'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        return {
            'is_valid': len(missing_columns) == 0,
            'missing_columns': missing_columns,
            'total_columns': len(df.columns),
            'total_rows': len(df)
        }
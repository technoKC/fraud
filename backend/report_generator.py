from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict
from io import BytesIO

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        
        # Define custom styles
        self.styles = getSampleStyleSheet()
        
        # Central Bank styles (Blue theme)
        self.styles.add(ParagraphStyle(
            name='CBTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),  # Deep blue
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CBSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),  # Medium blue
            spaceAfter=20
        ))
        
        # MANIT styles (Blue theme)
        self.styles.add(ParagraphStyle(
            name='MANITTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),  # Navy blue
            spaceAfter=30,
            alignment=TA_CENTER
        ))
    
    def generate_centralbank_report(self, df: pd.DataFrame, fraud_transactions: List[Dict], 
                                  transaction_statuses: Dict[str, str]) -> str:
        """Generate PDF report for Central Bank with enhanced styling"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"centralbank_fraud_report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF with custom page
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Add Central Bank logo and header
        logo_path = os.path.join("static", "centralbank.png")
        fraud_logo_path = os.path.join("static", "logo.png")
        
        # Header table with logos
        header_data = []
        if os.path.exists(fraud_logo_path) and os.path.exists(logo_path):
            fraud_logo = Image(fraud_logo_path, width=1*inch, height=1*inch)
            cb_logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
            header_data = [[fraud_logo, 'FRAUD DETECTION REPORT', cb_logo]]
        else:
            header_data = [['', 'FRAUD DETECTION REPORT', '']]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 24),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1e40af')),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Title and Bank Info
        story.append(Paragraph("Central Bank of India", self.styles['CBTitle']))
        story.append(Paragraph("Fraud Detection & Prevention Unit", self.styles['CBSubtitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata with blue background
        metadata = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Total Transactions Analyzed:', f'{len(df):,}'],
            ['Fraud Transactions Detected:', f'{len(fraud_transactions)}'],
            ['Fraud Rate:', f'{(len(fraud_transactions) / len(df) * 100):.2f}%' if len(df) > 0 else '0%'],
            ['Blocked Accounts:', f'{sum(1 for s in transaction_statuses.values() if s == "blocked")}'],
            ['Verified Accounts:', f'{sum(1 for s in transaction_statuses.values() if s == "verified")}']
        ]
        
        metadata_table = Table(metadata, colWidths=[3*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0f2fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['CBSubtitle']))
        summary_text = f"""
        The FraudShield AI system has analyzed {len(df):,} transactions and identified {len(fraud_transactions)} 
        potentially fraudulent transactions. The system uses advanced AI algorithms including pattern recognition, 
        anomaly detection, and network analysis to identify suspicious activities. 
        Current system accuracy stands at {((len(df) - len(fraud_transactions)) / len(df) * 100):.1f}%.
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fraud Transaction Details
        story.append(Paragraph("Critical Fraud Alerts - Top 15 Transactions", self.styles['CBSubtitle']))
        
        # Create fraud transactions table
        fraud_table_data = [['Transaction ID', 'Amount (₹)', 'Payer VPA', 'Risk Score', 'Status']]
        
        for txn in fraud_transactions[:15]:
            txn_id = txn['transaction_id']
            status = transaction_statuses.get(txn_id, "Pending")
            status_color = {
                'blocked': colors.red,
                'verified': colors.green,
                'pending': colors.orange
            }.get(status.lower(), colors.black)
            
            fraud_table_data.append([
                txn_id[:20] + "..." if len(txn_id) > 20 else txn_id,
                f"₹{txn['amount']:,.2f}",
                txn['payer_vpa'][:25] + "..." if len(txn['payer_vpa']) > 25 else txn['payer_vpa'],
                f"{txn.get('risk_score', 0)}%",
                status.capitalize()
            ])
        
        fraud_table = Table(fraud_table_data, colWidths=[2*inch, 1.2*inch, 2.5*inch, 1*inch, 1*inch])
        fraud_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (4, -1), 'CENTER'),
        ]))
        
        # Apply status colors
        for i, txn in enumerate(fraud_transactions[:15], start=1):
            txn_id = txn['transaction_id']
            status = transaction_statuses.get(txn_id, "Pending")
            if status.lower() == 'blocked':
                fraud_table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.red)]))
            elif status.lower() == 'verified':
                fraud_table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.green)]))
            else:
                fraud_table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.orange)]))
        
        story.append(fraud_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(
            "This is a system-generated report. For queries, contact Central Bank of India Fraud Detection Unit.",
            footer_style
        ))
        story.append(Paragraph(
            "Powered by FraudShield AI - Detect | Explain | Protect",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_manit_report(self, df: pd.DataFrame, loan_data: Dict[str, any],
                            transaction_statuses: Dict[str, str]) -> str:
        """Generate PDF report for MANIT Bhopal with blue theme"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manit_loan_report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Add MANIT logo and header
        manit_logo_path = os.path.join("static", "manit.png")
        fraud_logo_path = os.path.join("static", "logo.png")
        
        # Header with logos
        header_data = []
        if os.path.exists(fraud_logo_path) and os.path.exists(manit_logo_path):
            fraud_logo = Image(fraud_logo_path, width=1*inch, height=1*inch)
            manit_logo = Image(manit_logo_path, width=1.5*inch, height=1.5*inch)
            header_data = [[fraud_logo, 'LOAN FEE VERIFICATION REPORT', manit_logo]]
        else:
            header_data = [['', 'LOAN FEE VERIFICATION REPORT', '']]
        
        header_table = Table(header_data, colWidths=[2.5*inch, 3*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 20),  # Reduced font size
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1e3a8a')),
            ('PADDING', (0, 0), (-1, -1), 15),  # Add padding around content
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.8*inch))  # Increased spacing after header
        
        # Institute details with better spacing
        story.append(Paragraph("Maulana Azad National Institute of Technology", self.styles['MANITTitle']))
        story.append(Spacer(1, 0.2*inch))  # Add spacing after main title
        story.append(Paragraph("Bhopal, Madhya Pradesh", self.styles['Normal']))
        story.append(Paragraph("Student Loan Fee Verification System", self.styles['CBSubtitle']))
        story.append(Spacer(1, 0.5*inch))  # Increased spacing before summary
        
        # Summary statistics with blue theme
        summary_data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Total Loan Transactions:', f"{loan_data['total_transactions']}"],
            ['Transactions Received:', f"{loan_data['received']}"],
            ['Verified for Registration:', f"{loan_data['verified']}"],
            ['Pending Verification:', f"{loan_data['pending']}"],
            ['Verification Rate:', f"{loan_data['verification_rate']:.1f}%"],
            ['Total Amount Received:', f"₹{loan_data['total_amount_received']:,.2f}"],
            ['Total Amount Pending:', f"₹{loan_data['total_amount_pending']:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2563eb')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        story.append(PageBreak())
        
        # Department-wise Statistics
        story.append(Paragraph("Department-wise Loan Statistics", self.styles['CBSubtitle']))
        
        dept_table_data = [['Department', 'Total', 'Verified', 'Pending', 'Amount (₹)']]
        for dept, stats in loan_data['department_statistics'].items():
            if stats['total'] > 0:
                dept_table_data.append([
                    dept,
                    str(stats['total']),
                    str(stats['verified']),
                    str(stats['pending']),
                    f"₹{stats['amount']:,.0f}"
                ])
        
        dept_table = Table(dept_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2563eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(dept_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Student Transaction Details
        story.append(Paragraph("Student Transaction Details", self.styles['CBSubtitle']))
        
        # Separate transactions by status
        verified_txns = [t for t in loan_data['transactions'] if t['status'].lower() == 'verified']
        pending_txns = [t for t in loan_data['transactions'] if t['status'].lower() == 'pending']
        
        # Verified Transactions
        if verified_txns:
            story.append(Paragraph("Verified Transactions", self.styles['Heading3']))
            verified_table_data = [['Student ID', 'Name', 'Semester', 'Amount', 'Bank']]
            
            for txn in verified_txns[:10]:
                verified_table_data.append([
                    txn['student_id'],
                    txn['student_name'][:20] + "..." if len(txn['student_name']) > 20 else txn['student_name'],
                    txn['semester'],
                    f"₹{txn['amount']:,.0f}",
                    txn['bank_name']
                ])
            
            verified_table = Table(verified_table_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch, 1.5*inch])
            verified_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#22c55e')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ]))
            story.append(verified_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Pending Transactions
        if pending_txns:
            story.append(Paragraph("Pending Verification", self.styles['Heading3']))
            pending_table_data = [['Student ID', 'Name', 'Semester', 'Amount', 'Notes']]
            
            for txn in pending_txns[:10]:
                pending_table_data.append([
                    txn['student_id'],
                    txn['student_name'][:20] + "..." if len(txn['student_name']) > 20 else txn['student_name'],
                    txn['semester'],
                    f"₹{txn['amount']:,.0f}",
                    txn['verification_notes'][:30] + "..." if len(txn['verification_notes']) > 30 else txn['verification_notes']
                ])
            
            pending_table = Table(pending_table_data, colWidths=[1.2*inch, 1.8*inch, 0.8*inch, 1.2*inch, 2.5*inch])
            pending_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fb923c')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff7ed')]),
            ]))
            story.append(pending_table)
        
        # Footer
        story.append(Spacer(1, 1*inch))
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(
            "This report is generated for official use by MANIT Bhopal Administration",
            footer_style
        ))
        story.append(Paragraph(
            "Powered by FraudShield - Integrated with MANIT Student Services",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        
        return filepath
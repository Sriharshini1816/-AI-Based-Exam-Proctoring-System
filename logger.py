import csv
import os
from datetime import datetime
from collections import defaultdict

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab not installed - PDF reports disabled")


class ProctorLogger:
    def __init__(self, filename="proctoring_audit_trail.csv"):
        self.filename = filename
        self.evidence_dir = "evidence"

        # Create evidence folders
        os.makedirs(f"{self.evidence_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.evidence_dir}/clips", exist_ok=True)

        # Create CSV file if not exists
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Violation_Type", "Severity", "Evidence_Ref"])

    # --------------------------
    # Log violation with severity
    # --------------------------
    def log_violation(self, violation_type, evidence_ref="Pending", severity="MEDIUM"):
        timestamp = datetime.now().isoformat(timespec='milliseconds')

        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, violation_type, severity, evidence_ref])

        print(f"[{'🔴' if severity == 'HIGH' else '🟡'} {severity}] {timestamp} - {violation_type}")

    # --------------------------
    # Get Violation Summary
    # --------------------------
    def get_summary(self):
        summary = {}
        severity_count = defaultdict(int)

        if not os.path.exists(self.filename):
            return summary, severity_count

        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                v_type = row["Violation_Type"]
                severity = row.get("Severity", "MEDIUM")
                
                summary[v_type] = summary.get(v_type, 0) + 1
                severity_count[severity] += 1

        return summary, severity_count

    # --------------------------
    # Get all violations from CSV
    # --------------------------
    def get_all_violations(self):
        violations = []
        if not os.path.exists(self.filename):
            return violations

        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                violations.append(row)

        return violations

    # --------------------------
    # Generate Professional PDF Report
    # --------------------------
    def generate_forensic_report(self, student_id="Candidate_001"):
        if not REPORTLAB_AVAILABLE:
            print("⚠️ reportlab not available - skipping PDF generation")
            return None

        report_name = f"evidence/Forensic_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            # PDF Setup
            doc = SimpleDocTemplate(report_name, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=12
            )
            
            high_alert_style = ParagraphStyle(
                'HighAlert',
                parent=styles['Normal'],
                textColor=colors.red,
                fontSize=11,
                spaceAfter=10
            )

            # Title
            elements.append(Paragraph("EXAM PROCTORING FORENSIC REPORT", title_style))
            elements.append(Spacer(1, 0.3*inch))

            # Header Info
            header_data = [
                ["Candidate ID:", student_id],
                ["Report Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["Report Type:", "Automated Proctoring Analysis"]
            ]
            
            header_table = Table(header_data)
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 0.3*inch))

            # Violations Summary
            summary, severity_count = self.get_summary()
            
            elements.append(Paragraph("VIOLATIONS SUMMARY", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            summary_data = [["Violation Type", "Count", "Severity Level"]]
            for v_type, count in summary.items():
                summary_data.append([v_type, str(count), "HIGH" if count > 3 else "MEDIUM"])
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))

            # Detailed violations
            elements.append(Paragraph("INCIDENT TIMELINE", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            violations = self.get_all_violations()
            if violations:
                timeline_data = [["Time", "Incident", "Severity", "Evidence"]]
                for v in violations[-30:]:  # Last 30 violations
                    timeline_data.append([
                        v['Timestamp'][:19],
                        v['Violation_Type'],
                        v.get('Severity', 'MEDIUM'),
                        os.path.basename(v.get('Evidence_Ref', 'N/A'))
                    ])
                
                timeline_table = Table(timeline_data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
                timeline_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elements.append(timeline_table)

            # Build PDF
            doc.build(elements)
            print(f"📄 Forensic Report Generated: {report_name}")
            return report_name

        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return None


# --------------------------
# Event logger (for audio + system events)
# --------------------------
def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("events.log", "a") as file:
        file.write(f"[{timestamp}] {message}\n")

    print(f"[EVENT] {message}")

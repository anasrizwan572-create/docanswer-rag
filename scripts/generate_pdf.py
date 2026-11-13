"""
Script to generate a realistic 18-20 page corporate HR Policy Handbook PDF and Markdown.
Acme Technologies Inc. - Global Employee Handbook (2026 Edition)
"""
import os
import re
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MD_FILE = DATA_DIR / "acme_corp_hr_policy.md"
PDF_FILE = DATA_DIR / "acme_corp_hr_policy.pdf"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and stamp Page X of Y footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        # Header on pages after page 1
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Acme Technologies Inc. — Global Employee Handbook (2026 Edition)")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "Document Ref: ACME-HR-2026-V4.2")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, page_str)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — STRICTLY FOR INTERNAL ACME EMPLOYEE USE")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, letter[0] - 54, 48)
        self.restoreState()


HANDBOOK_MD = """# Acme Technologies Global HR Policies and Employee Handbook (2026 Edition)

**Document Reference:** ACME-HR-2026-V4.2  
**Effective Date:** January 1, 2026  
**Applicability:** All Full-Time, Part-Time, and Fixed-Term Employees  
**Classification:** Confidential - Internal Company Policy  
**Approved By:** Board of Directors & Chief People Officer  

---

## Section 1: General Employment Principles & Classifications

### 1.1 Purpose and At-Will Relationship
This Employee Handbook outlines the operating personnel policies, standards of conduct, and employment terms for Acme Technologies Inc. ("Acme" or "the Company"). Except as otherwise provided in an individual written employment contract signed by the Chief Executive Officer, all employment at Acme is "at-will." Either the employee or the Company may terminate the employment relationship at any time, with or without cause, subject to the applicable notice periods set forth in Section 9. Nothing in this handbook constitutes an express or implied contract of continued employment.

### 1.2 Employment Classifications
For benefits eligibility, compensation structure, and statutory compliance, employees are classified under the following categories:
- **Regular Full-Time (Class A):** Employees regularly scheduled to work at least 40 hours per calendar week. Eligible for all standard benefits described in Section 4.
- **Regular Part-Time (Class B):** Employees regularly scheduled to work between 20 and 39 hours per week. Eligible for statutory benefits and pro-rated annual leave (see Section 3.1). Not eligible for tuition assistance under Section 4.4.
- **Temporary / Seasonal (Class C):** Employees engaged for an anticipated duration not exceeding 6 consecutive months. Class C employees are not eligible for paid parental leave, tuition assistance, or severance pay.
- **Contractors and Independent Consultants:** Non-payroll personnel governed strictly by Master Services Agreements (MSAs). No company policy herein confers employment rights or employee benefits upon independent contractors.

### 1.3 Probationary Period
All newly hired Class A and Class B employees are subject to a mandatory introductory probationary period of ninety (90) calendar days from their effective start date. During the probationary period:
1. Performance, punctuality, and cultural alignment will be formally evaluated at day 45 and day 85.
2. The probationary notice period specified in Section 9.1 applies to terminations initiated by either party.
3. Employees may not take discretionary annual leave during probation, except when pre-approved in writing during the hiring offer stage by the Hiring Manager and HR Director.
4. Remote work privileges remain restricted during probation pursuant to Section 2.2.

---

## Section 2: Working Hours, Hybrid & Remote Work Policy

### 2.1 Standard Working Hours & Core Collaboration Hours
Acme's standard operating schedule comprises a 40-hour work week, Monday through Friday. To facilitate cross-functional collaboration across time zones, the Company designates Core Collaboration Hours from **10:00 AM to 4:00 PM Eastern Standard Time (EST)**. All active employees, regardless of physical work location, must remain accessible via Slack, email, and Google Meet during Core Collaboration Hours, excluding scheduled lunch breaks.

### 2.2 Hybrid & Remote Work Eligibility
Acme operates on a flexible hybrid model. Eligibility for remote and hybrid working arrangements is governed by the following criteria:
1. **Tenure Requirement:** Employees must successfully complete their 90-day probationary period (Section 1.3) prior to submitting a recurring remote work request, except when hired under an explicit "Permanent Remote Agreement" executed at the offer stage.
2. **Office Attendance Baseline:** Regular full-time employees assigned to an Acme office hub must work on-site at least two (2) designated days per week (typically Tuesday and Thursday), unless granted an accommodation under Section 2.4 or Section 13.
3. **Performance Prerequisite:** Employees currently placed on a Performance Improvement Plan (PIP) under Section 8.2 are ineligible for remote work and must attend the office five days a week until successful PIP exit.

### 2.3 Remote Work Stipend & Equipment
To maintain an ergonomic and secure home working environment:
- **One-Time Home Office Setup Allowance:** Full-time remote employees (or hybrid employees working at least 2 days remote) are eligible for a one-time reimbursement of up to **$800 USD** for desk, ergonomic chair, and monitor purchases. Receipts must be submitted within sixty (60) days of hire via Concur (see Section 5.1).
- **Monthly Connectivity Stipend:** Qualified remote employees receive a non-taxable monthly internet subsidy of **$60 USD**, disbursed automatically through regular payroll.
- **Equipment Ownership:** All computer laptops, monitors, security tokens, and peripherals purchased with company funds remain Acme property and must be returned within forty-eight (48) hours of employment termination (see Section 9.4).

### 2.4 Work from Anywhere (Temporary Remote Work)
Employees may request to work from an alternate domestic or international location for up to twenty (20) business days per calendar year ("Work from Anywhere" privilege).
- **Approval Chain:** Requires written approval from the Department Vice President and People Operations at least thirty (30) days in advance.
- **Tax and Legal Restrictions:** Work from Anywhere is strictly prohibited in countries subject to OFAC sanctions or jurisdictions where Acme does not maintain a registered corporate presence if the duration exceeds 30 continuous calendar days.

---

## Section 3: Leave, Time Off & Absence Policies

### 3.1 Annual Paid Time Off (PTO) Entitlement
Acme grants paid annual leave based on completed years of continuous service (tenure) and job grade. PTO accrues semi-monthly on each payroll cycle starting from day one of employment, but cannot be utilized during the probationary period (Section 1.3).

| Continuous Service Tenure | Individual Contributor (Levels 1-3) | Senior & Lead (Levels 4-5) | Management & Director (Level 6+) |
| :--- | :--- | :--- | :--- |
| **0 to 12 Months (< 1 year)** | 15 working days / year | 18 working days / year | 22 working days / year |
| **1 Year to 3 Years** | 20 working days / year | 22 working days / year | 25 working days / year |
| **3 Years to 5 Years** | 23 working days / year | 25 working days / year | 27 working days / year |
| **5+ Years** | 28 working days / year | 30 working days / year | 32 working days / year |

#### 3.1.1 PTO Carry-Over and Expiry
A maximum of five (5) accrued but unused PTO days may be carried forward into the subsequent calendar year. Any carried-over days must be exhausted by March 31 of that following year; any balance remaining beyond March 31 shall be forfeited without financial compensation, except where prohibited by local labor regulations.

#### 3.1.2 Blackout Periods
PTO requests exceeding two (2) consecutive weeks require approval from the Department Vice President at least six (6) weeks in advance. The Company reserves the right to impose departmental blackout periods during critical operational milestones (e.g., Annual Financial Close between January 5 and January 20 for Finance; Product Launch weeks for Engineering).

### 3.2 Sick Leave and Medical Certification
Health and wellbeing are essential to sustainable high performance.
1. **Annual Allocation:** Full-time employees receive ten (10) fully paid sick leave days per calendar year, credited on January 1.
2. **Probationary Usage:** Unlike PTO, sick leave may be utilized during the 90-day probationary period for legitimate personal medical illness or to care for an immediate family member.
3. **Medical Certificate Threshold:** A valid medical certificate issued by a licensed healthcare practitioner is mandatory for:
   - Any sick leave absence lasting three (3) or more consecutive business days;
   - Any single sick day taken immediately preceding or succeeding a scheduled public holiday or approved PTO day;
   - Repeated short-term sick absences exceeding six (6) instances within any rolling twelve-month timeframe.
4. **Failure to Provide Proof:** Failure to furnish a compliant medical note within forty-eight (48) hours of returning to duty will result in the absence being classified as Unexcused Unpaid Leave, triggering the disciplinary escalation process in Section 8.2.

### 3.3 Parental Leave Policy
Acme provides progressive, gender-neutral parental leave to support new parents welcoming a child through birth, adoption, or foster placement.
- **Primary Caregiver Leave:** Eligible employees who have completed at least twelve (12) months of continuous service are entitled to sixteen (16) weeks of 100% paid parental leave.
- **Secondary Caregiver Leave:** Eligible employees who have completed at least twelve (12) months of continuous service are entitled to six (6) weeks of 100% paid parental leave.
- **Tenure Exception (< 12 Months):** Employees with less than twelve (12) months of continuous service at the time of the child's birth/placement receive six (6) weeks of paid leave for primary caregivers and two (2) weeks for secondary caregivers.
- **Utilization Window:** Parental leave must be taken within twelve (12) months following the date of birth, adoption, or foster placement. It may be taken continuously or in two separate blocks of no less than two weeks each.

### 3.4 Bereavement Leave
Employees may take paid bereavement leave in the event of the loss of a family member:
- **Immediate Family (Spouse, Child, Parent, Sibling):** Up to five (5) consecutive paid working days.
- **Extended Family (Grandparent, Grandchild, In-laws):** Up to three (3) consecutive paid working days.
- **Additional Unpaid Days:** Employees requiring international travel for memorial services may request up to five (5) additional unpaid days, subject to manager approval.

### 3.5 Jury Duty and Civic Service
Employees summoned for mandatory jury service receive full pay for up to ten (10) working days per occurrence. The summons notice must be uploaded to the HR portal within three (3) business days of receipt.

---

## Section 4: Employee Benefits, Wellness & Education

### 4.1 Health, Dental, and Vision Insurance
Acme provides group medical, dental, and vision insurance coverage to all Class A full-time employees and their eligible dependents.
- **Effective Date:** Coverage commences on the first calendar day of the month following the employee's official start date.
- **Premium Subsidies:** Acme subsidizes 90% of the employee's monthly health premium and 75% of dependent premiums for the standard PPO and HDHP tiers. Premium contributions for executive-tier comprehensive plans are subsidized at 80% for both employee and dependents.

### 4.2 Retirement Plan: 401(k) Matching and Vesting
The Company offers a traditional and Roth 401(k) savings program administered through Vanguard.
1. **Company Match:** Acme matches 100% of employee contributions up to the first 4% of base salary, plus 50% of the next 2% of base salary (maximum effective match of 5% on a 6% employee contribution).
2. **Vesting Schedule:** Employee contributions are always 100% vested immediately. Acme matching contributions vest according to the following graduated schedule based on completed years of continuous service:

| Completed Continuous Service | Vested Percentage of Employer Match |
| :--- | :--- |
| **Less than 1 Year (< 12 Months)** | 0% (Fully unvested) |
| **1 Year to 2 Years** | 25% |
| **2 Years to 3 Years** | 50% |
| **3 Years to 4 Years** | 75% |
| **4+ Years** | 100% (Fully vested) |

*Exception:* In the event of Company dissolution, involuntary reduction in force (RIF) under Section 9.3, or death of the employee, all employer matching funds vest immediately at 100%.

### 4.3 Life and Disability Insurance
Acme funds 100% of the premium cost for:
- Basic Life and Accidental Death & Dismemberment (AD&D) equal to 2x annual base salary (capped at $500,000 USD).
- Short-Term Disability (STD) providing 66.7% of weekly earnings up to 26 weeks after a 7-day elimination period.
- Long-Term Disability (LTD) providing 60% of monthly earnings until retirement age for qualifying permanent conditions.

### 4.4 Tuition Assistance & Continuing Education
Acme invests in continuous employee development through our Education Assistance Program.
1. **Annual Cap:** Up to **$5,250 USD** per calendar year for pre-approved accredited degree programs, professional certifications, or technical courses relevant to the employee's current or prospective role.
2. **Tenure Requirement:** Only regular full-time employees with at least twelve (12) months of continuous service are eligible.
3. **Grade Requirement:** Reimbursement requires a minimum grade of "B" (or "Pass" for pass/fail certifications).
4. **Retention Clawback:** If an employee voluntarily resigns from Acme within twenty-four (24) months following receipt of tuition reimbursement, the employee must repay 100% of the tuition funds received during the preceding 12 months, and 50% of funds received between 13 and 24 months prior to resignation. This amount may be deducted from final salary payments in accordance with Section 9.4.

---

## Section 5: Travel, Meals & Business Expense Reimbursement

### 5.1 Expense Submission Principles
All legitimate, reasonable business expenses incurred directly in the discharge of company responsibilities will be reimbursed.
- **Reporting Window:** Expenses must be submitted via the Concur expense portal within thirty (30) calendar days of incurring the expense, accompanied by itemized tax receipts. Expenses submitted after sixty (60) days will be rejected and will not be reimbursed.
- **Receipt Threshold:** An itemized receipt is strictly mandatory for any individual expense item exceeding **$25.00 USD**. Credit card statements alone do not satisfy audit requirements.

### 5.2 Travel Allowances: Airfare and Lodging
1. **Air Travel Class:**
   - Domestic Flights (under 6 hours flight time): Economy Class / Coach only.
   - International Flights or Long-Haul Domestic (flight duration strictly exceeding six (6) continuous hours): Premium Economy is permitted.
   - Business Class: Strictly prohibited unless travel is intercontinental (>10 hours duration) AND pre-authorized in writing by the Chief Financial Officer (CFO).
2. **Lodging Guidelines:** Hotel accommodations must be booked at standard business hotels (e.g., Marriott, Hilton, Hyatt) at rates not exceeding the following nightly limits (exclusive of local taxes):
   - Tier 1 Cities (New York, San Francisco, London, Tokyo, Zurich): **$320 USD / night**.
   - Tier 2 Cities (Chicago, Austin, Boston, Seattle, Berlin, Singapore): **$240 USD / night**.
   - All Other Locations: **$180 USD / night**.

### 5.3 Daily Meal Per Diem & Entertainment
Employees traveling on authorized business trips may claim meal reimbursements subject to the maximum daily per diem caps set forth below:

| Expense Category | Daily Cap (USD) | Single Meal Guidelines |
| :--- | :--- | :--- |
| **Breakfast** | $18.00 | Applicable if travel begins before 7:00 AM |
| **Lunch** | $25.00 | Applicable during full-day travel or inter-office visits |
| **Dinner** | $37.00 | Applicable if travel extends past 7:30 PM |
| **Total Daily Per Diem Maximum** | **$75.00** | Cumulative limit for food & beverage per traveler |

#### 5.3.1 Alcohol Policy
Alcoholic beverages are non-reimbursable under daily travel per diems. *Exception:* Reasonable alcoholic beverages consumed during pre-approved client entertainment dinners are reimbursable provided a Senior Vice President or C-level executive attends and signs off on the expense report with the business purpose and attendee roster documented.

---

## Section 6: Code of Conduct, Workplace Ethics & Conflicts

### 6.1 Gifts, Hospitality, and Anti-Bribery
Acme strictly adheres to the U.S. Foreign Corrupt Practices Act (FCPA) and the UK Bribery Act.
- **Receiving Gifts:** Employees may not accept gifts, services, discounts, or entertainment from current or prospective vendors, partners, or clients with an estimated value exceeding **$50.00 USD**.
- **Aggregate Limit:** Total gifts from any single commercial entity may not exceed **$150.00 USD** within a single calendar year.
- **Cash and Cash Equivalents:** Accepting cash, prepaid cards, or securities is strictly forbidden regardless of amount and constitutes gross misconduct under Section 8.3.
- **Exceptions:** Promotional items of nominal value bearing a vendor logo (e.g., pens, notepads) are exempt from reporting.

### 6.2 Conflicts of Interest & Outside Employment
Employees owe an undivided duty of commercial loyalty to Acme.
1. **Secondary Employment (Moonlighting):** Full-time employees are prohibited from engaging in external commercial employment, consulting, board directorships, or personal enterprise that conflicts with Acme's business interests, competes with Acme products, or consumes working hours designated under Section 2.1.
2. **Written Disclosure:** Any proposed external engagement or advisory role requires advance written disclosure and explicit authorization from the Chief Legal Officer (CLO) and Chief People Officer (CPO).
3. **Personal Relationships in Reporting Lines:** Direct supervisory or managerial relationships between romantic partners, spouses, or immediate relatives are prohibited. If such a relationship develops, both employees must inform HR within fourteen (14) days to facilitate a non-punitive departmental transfer.

---

## Section 7: Anti-Harassment, Discrimination & Reporting Procedure

### 7.1 Zero Tolerance Policy
Acme maintains an uncompromising zero-tolerance policy regarding sexual harassment, workplace bullying, racial discrimination, retaliatory actions, or harassment based on race, color, religion, sexual orientation, gender identity, national origin, age, disability, or genetic status.

### 7.2 Reporting Channels and Timelines
Any employee who experiences, witnesses, or reasonably suspects discriminatory conduct or harassment must report the situation immediately through any of the following designated avenues:
1. **Direct Notification:** The employee's direct Manager or Department Vice President.
2. **People Operations:** Dedicated confidential HR intake email: `ethics-hotline@acme-tech.internal`.
3. **Anonymous Whistleblower Hotline:** Toll-free 24/7 hotline at `1-800-555-ACME-SAFE` or online at `acme.ethicspoint.internal`.
4. **Reporting Deadline:** Reports should be filed as promptly as feasible, and no later than **ten (10) business days** following the alleged incident, although late reports will still be thoroughly investigated.

### 7.3 Formal Investigation Process
Upon receipt of a complaint under Section 7.2, People Operations and Legal initiate the following structured protocol:
1. **Intake & Triage (Within 24 Hours):** The complainant is interviewed by an independent investigator; interim protective measures (e.g., paid administrative leave, reassignment of reporting lines) are enacted to safeguard the complainant.
2. **Fact-Finding & Evidence Collection (Days 2 to 10):** The investigator conducts private interviews with the respondent and relevant witnesses, reviewing digital communications, badge access logs, and Slack archives.
3. **Determination and Findings Report (Within 15 Business Days):** A written findings report is presented to the Chief Legal Officer and Chief People Officer.
4. **Disciplinary Enforcement:** If substantiated, punitive actions up to and including immediate termination for gross misconduct (Section 8.3) are implemented without delay.

### 7.4 Absolute Non-Retaliation Guarantee
Acme guarantees that no employee will suffer adverse employment repercussions, career detriment, or workplace hostility for filing a good-faith report or cooperating in an investigation under Section 7. Any manager or peer found to have retaliated against a complainant or witness will be subject to immediate summary dismissal.

---

## Section 8: Performance Management & Disciplinary Process

### 8.1 Performance Reviews and Check-ins
Performance is formally assessed twice annually: Mid-Year Check-in (June) and Annual Comprehensive Review (December). Ratings directly influence merit salary adjustments, promotion eligibility, and annual incentive bonuses.

### 8.2 Progressive Disciplinary Framework
Where employee performance, behavior, or attendance fails to meet acceptable company standards, Acme applies a progressive four-stage disciplinary ladder:
1. **Stage 1 - Documented Verbal Counseling:** Formal discussion with manager outlining deficiencies, recorded in the employee's HR dossier for six (6) months.
2. **Stage 2 - Formal Written Warning:** If deficiencies persist after 30 days, a written warning is issued outlining specific remediation objectives and consequences.
3. **Stage 3 - Performance Improvement Plan (PIP):**
   - Duration: The standard PIP duration is **thirty (30) calendar days**, extendable to sixty (60) days only upon written consent of the HR Director.
   - Terms: The employee must meet weekly with their manager to review metric milestones.
   - Remote Restrictions: Remote work privileges are suspended for the duration of the PIP (see Section 2.2).
4. **Stage 4 - Termination of Employment:** Failure to satisfy PIP milestones at the conclusion of the 30-day term results in immediate separation of employment under Section 9.2.

### 8.3 Gross Misconduct & Immediate Summary Dismissal
Progressive discipline does not apply to acts of gross misconduct. The Company reserves the legal right to terminate employment immediately without notice or severance pay for offenses including, but not limited to:
- Physical violence, threats, or weapons on company premises;
- Theft, fraud, embezzlement, or falsification of business/expense records (Section 5.1);
- Unlawful workplace harassment or retaliation (Section 7.4);
- Intentional exfiltration or transmission of proprietary code, customer PII, or trade secrets (Section 10.2);
- Commercial bribery or accepting prohibited gifts (Section 6.1);
- Operating company machinery or vehicles under the influence of illegal drugs or alcohol.

---

## Section 9: Termination, Resignation & Notice Periods

### 9.1 Voluntary Resignation Notice Periods
Employees wishing to resign from Acme in good standing must submit written notice to their manager and HR. Required notice periods depend on job classification and level:

| Employee Classification / Level | Mandatory Minimum Notice Period |
| :--- | :--- |
| **Probationary Employees (All Levels)** | 1 calendar week (7 days) |
| **Individual Contributors (Levels 1 to 3)** | 2 calendar weeks (14 days) |
| **Senior, Lead, & Managers (Levels 4 to 5)** | 4 calendar weeks (28 days) |
| **Directors, VPs, and Officers (Level 6+)** | 8 calendar weeks (56 days) |

#### 9.1.1 Garden Leave Provision
Acme reserves the right, at its sole discretion, to waive the requirement that an employee physically work through their notice period. Under "Garden Leave," the employee remains on full payroll and benefits through the notice expiration date but is relieved of active duties and restricted from contacting clients or accessing company IT systems.

### 9.2 Involuntary Dismissal for Performance / Cause
Employees dismissed under Stage 4 of Progressive Discipline (Section 8.2) receive statutory or contractually required notice (typically two weeks' base salary in lieu of notice). No severance package is provided for performance separations.

### 9.3 Involuntary Redundancy & Severance Calculation
In the event of an involuntary organizational restructuring, departmental downsizing, or corporate redundancy, eligible full-time employees receive severance pay calculated as follows:
- **Base Severance Formula:** One (1) week of base salary for each completed continuous year of service, with a minimum guaranteed threshold of two (2) weeks' pay.
- **Severance Cap:** Total severance entitlement shall not exceed a maximum ceiling of **sixteen (16) weeks' base pay**, regardless of total tenure length.
- **COBRA Subsidy:** Acme subsidizes COBRA healthcare premiums for three (3) months following the separation date.
- **Exclusions:** Severance pay is strictly unavailable to employees terminated for gross misconduct (Section 8.3), voluntary resignations, or temporary/contract personnel (Section 1.2).

### 9.4 Final Pay & Return of Company Property
- **Payroll Settlement:** Final compensation, including earned base wages and accrued unused PTO (capped pursuant to Section 3.1.1), will be disbursed on the next regular payroll date or earlier where required by state statute.
- **Deductions:** Any outstanding debts, unreturned equipment costs, or tuition assistance retention clawbacks (Section 4.4) will be offset against final payments where legally permissible.
- **Hardware & Asset Return:** All assigned laptops, monitors, corporate credit cards, security badges, and physical documentation must be returned to Acme IT/People Operations within **forty-eight (48) hours** of the termination timestamp.

---

## Section 10: Information Security, Intellectual Property & Data Privacy

### 10.1 Acceptable Use of IT Resources
Company hardware, networks, communication tools, and data stores are provided strictly for official business activities. Incidental personal use is permitted provided it does not compromise network security, consume excessive bandwidth, or violate ethical guidelines.
- **Zero Privacy Expectation:** Employees possess no subjective or legal expectation of privacy regarding communications transmitted over, stored upon, or accessed through Acme systems (including Slack, corporate email, Google Drive, and GitHub). Acme reserves the right to monitor, inspect, and archive all digital activity.
- **Password Hygiene & 2FA:** Multi-factor authentication (MFA/2FA) through company-approved security tokens (e.g., YubiKey, Okta Verify) is mandatory for all system access. Passwords must be at least 16 characters in length and rotated every 90 days.

### 10.2 Intellectual Property Assignment & Confidentiality
1. **Invention Assignment:** All inventions, designs, source code, documentation, algorithms, and business discoveries conceived, authored, or reduced to practice by employees during their tenure—whether during standard work hours or using Acme assets—are the exclusive intellectual property of Acme Technologies Inc. under the "work-for-hire" doctrine.
2. **Proprietary Information Agreement (PIA):** Employees must execute the standard Acme PIA upon hire. The obligation to protect trade secrets, client financial data, and proprietary technical designs endures indefinitely following termination of employment.
3. **AI Tooling & Code Generation Policy:** Employees are strictly prohibited from pasting proprietary Acme source code, internal architectural specifications, or confidential customer data into unapproved third-party public AI platforms (e.g., public ChatGPT, Claude, Copilot). Only enterprise-licensed AI tools operating under verified non-training agreements with Acme may be utilized for engineering or operational tasks.

---

## Section 11: Workplace Health, Safety & Emergency Protocols

### 11.1 General Occupational Health and Safety
Acme is committed to providing a secure, healthy, and compliant physical work environment in accordance with the Occupational Safety and Health Administration (OSHA) regulations and local municipal building codes. Every employee shares responsibility for maintaining workplace safety:
- **Hazard Reporting:** Employees must report any physical safety hazard, equipment malfunction, slippery floor, or blocked fire exit immediately to Workplace Facilities via email at `facilities@acme-tech.internal` or via Slack channel `#facilities-help`.
- **Emergency Exits:** Fire exit doors, emergency stairwells, and electrical panels must remain unobstructed by boxes, furniture, or equipment at all times.

### 11.2 Reporting Workplace Injuries and Worker's Compensation
1. **Immediate Notification:** Any workplace injury, accidental fall, or occupational illness occurring on company premises or during authorized work activities must be reported to the employee's manager and the Safety Coordinator within **twenty-four (24) hours** of occurrence, regardless of apparent severity.
2. **Medical Treatment:** In emergencies, immediate medical attention must be sought via 911. For non-emergency work-related injuries, employees will be referred to an approved occupational medical clinic within the Company's Workers' Compensation medical provider network.
3. **Workers' Compensation Claims:** People Operations coordinates statutory Workers' Compensation claim filings. Failure to report injuries within statutory reporting windows (maximum 3 business days) may jeopardize state insurance claim validity.

### 11.3 Ergonomic Assessments and Wellness Ergonomics
Acme offers ergonomic workstation assessments conducted by certified ergonomic specialists.
- Both on-site hub workers and remote workers are entitled to an annual remote ergonomic evaluation.
- Remediation hardware recommendations (such as ergonomic vertical mice, split mechanical keyboards, or sit-stand desk convertors) up to **$250 USD** are funded directly through Workplace Facilities above and beyond the one-time home office allowance in Section 2.3.

### 11.4 Emergency Evacuation and Disaster Response
- **Evacuation Drills:** Mandatory building evacuation drills occur biannually at all office hubs. Participation is strictly compulsory for all on-site personnel.
- **Floor Wardens:** Designated Floor Safety Wardens are trained in first aid, CPR, and automated external defibrillator (AED) operation.
- **Emergency Notification System:** Acme utilizes the Everbridge mass emergency notification platform. In the event of extreme weather, active threat, or facility closure, automated text messages, automated phone calls, and Slack notifications are broadcasted to all employees.

---

## Section 12: Communication, Social Media & Media Relations

### 12.1 Authorized Company Spokespersons
To ensure accurate, unified, and legally vetted public communications:
- Only designated executive officers (CEO, CFO, CPO) and the Corporate Communications Director are authorized to deliver public statements, grant press interviews, or respond to journalist inquiries on behalf of Acme Technologies.
- Any media inquiry received by an individual contributor or manager—including inquiries from print journalists, podcasters, bloggers, or television reporters—must be forwarded within two (2) hours to `press@acme-tech.internal` without editorial commentary.

### 12.2 Personal Social Media Conduct
Acme respects employees' First Amendment freedoms and personal digital expression on platforms such as LinkedIn, X (Twitter), Facebook, Instagram, and Reddit. However, personal digital conduct must adhere to standard ethical safeguards:
1. **Mandatory Disclaimer:** Employees referencing Acme Technologies in their social media bio or posting commentary regarding enterprise software, cybersecurity, or tech industry trends must include a visible disclaimer: *"The views expressed here are my own and do not represent the official stance or policy of Acme Technologies Inc."*
2. **Protection of Confidential Information:** Employees must never publish, photograph, or disclose non-public company financial results, unreleased product roadmaps, client identities, security vulnerabilities, or internal executive memos.
3. **Professional Decorum:** Employees may not post defamatory, harassing, discriminatory, or threatening content regarding Acme colleagues, customers, or business partners. Violations will be handled under Section 7 and Section 8.3.

### 12.3 Speaking Engagements and Academic Publications
Employees invited to present at external industry conferences, technical panels, or publish technical whitepapers referencing company methodologies or architecture must obtain advance written approval from their Department Vice President and Corporate Communications at least fourteen (14) business days prior to the event.

---

## Section 13: Workplace Accommodations & Religious Observance

### 13.1 Americans with Disabilities Act (ADA) Reasonable Accommodations
Acme provides reasonable workplace accommodations to qualified individuals with documented physical, mental, sensory, or cognitive disabilities, unless doing so would impose an undue operational hardship on the Company.
- **Request Procedure:** An employee seeking an accommodation should contact People Operations via `accommodations@acme-tech.internal` or complete the confidential ADA Request Form on the HR portal.
- **Interactive Process:** People Operations will engage in a collaborative, interactive dialogue with the employee and, where appropriate, request relevant medical documentation verifying functional limitations and suggested accommodation options.
- **Confidentiality:** All medical documentation submitted during the accommodation process is stored in a secure, confidential medical file segregated from the general personnel folder.

### 13.2 Religious Observance and Floating Holidays
Acme respects the religious beliefs and practices of all team members:
1. **Religious Accommodation:** Employees may request adjustments to working schedules, shift modifications, or dress code exemptions for religious observances. Requests should be submitted to the employee's manager at least two (2) weeks in advance.
2. **Floating Religious / Cultural Days:** In addition to standard observed corporate public holidays, Acme grants two (2) paid Floating Cultural Holidays per calendar year. These days may be utilized for religious, cultural, or personal heritage observances upon written notice to the manager. Floating holidays do not roll over from year to year.

### 13.3 Lactation Accommodations
In compliance with the federal PUMP Act and state nursing protections, Acme provides dedicated, comfortable, and private Lactation Rooms in every office hub:
- **Amenities:** Each lactation suite is shielded from view, free from intrusion, equipped with an electrical outlet, comfortable seating, a sink, and a dedicated refrigerator for breast milk storage.
- **Break Time:** Nursing employees are entitled to reasonable paid break time as frequently as needed for up to one (1) year following the birth of a child.

---

## Section 14: Compensation, Overtime & Payroll Administration

### 14.1 Fair Labor Standards Act (FLSA) Classifications
All employee positions at Acme are evaluated and designated as either Exempt or Non-Exempt under the Fair Labor Standards Act (FLSA):
- **Exempt Employees:** Generally executive, administrative, professional, or software engineering roles whose job duties and weekly salary meet statutory exemption standards. Exempt employees receive an established base salary regardless of hours worked and are ineligible for overtime compensation.
- **Non-Exempt Employees:** Positions entitled to minimum wage and overtime pay under statutory rules. Non-exempt employees must accurately log all working hours through the company timekeeping system (ADP Time).

### 14.2 Timekeeping and Overtime Authorization for Non-Exempt Staff
1. **Accurate Recording:** Non-exempt employees must record exact arrival, departure, and meal break timestamps daily. Working "off-the-clock" is strictly forbidden and constitutes a serious disciplinary violation.
2. **Overtime Calculation:** Overtime is compensated at 1.5 times the employee's regular hourly rate for all hours worked in excess of forty (40) hours in a standard work week.
3. **Prior Authorization:** Overtime work must be pre-approved in writing by the direct supervisor prior to commencement. Working unauthorized overtime will be paid in compliance with federal law, but may result in disciplinary counseling under Section 8.2 for failure to adhere to supervisory instructions.

### 14.3 Payroll Cycles and Direct Deposit
- **Pay Frequency:** Acme administers payroll on a semi-monthly basis, resulting in twenty-four (24) pay periods per calendar year. Paydays occur on the **15th** and the **last business day** of each calendar month. When a payday falls on a weekend or bank holiday, funds are deposited on the immediately preceding business day.
- **Direct Deposit:** Direct electronic bank deposit is strongly encouraged. Employees may allocate payroll deposits across up to three (3) distinct checking or savings accounts through the ADP Employee Self-Service portal.
- **Payroll Auditing & Discrepancies:** Employees are responsible for reviewing pay stubs. Any perceived wage discrepancies or incorrect deductions must be flagged to `payroll@acme-tech.internal` within thirty (30) days for immediate payroll correction.

---

## Section 15: Employee Dispute Resolution & Grievance Procedure

### 15.1 Informal Conflict Resolution
Acme encourages an open, transparent culture where workplace friction, interpersonal misunderstandings, and procedural concerns are resolved collegially at the lowest managerial level possible. Employees experiencing friction with a colleague or manager are encouraged to schedule an informal discussion directly or request facilitated mediation through People Operations.

### 15.2 Formal Three-Step Grievance Procedure
When informal efforts fail to resolve a substantial dispute, or where the matter involves allegations of unfair treatment, policy misapplication, or wrongful disciplinary sanctions (excluding harassment claims handled under Section 7), the employee may invoke the formal grievance procedure:
1. **Step 1 - Formal Written Grievance:** Within fourteen (14) calendar days of the event, the employee submits a written grievance letter to their Department Director and HR Business Partner. A formal meeting is convened within seven (7) business days, followed by a written response within five (5) days.
2. **Step 2 - Executive Review:** If unsatisfied with Step 1, the employee may appeal within seven (7) days to the Chief People Officer (CPO). The CPO conducts an independent review and issues a determination within ten (10) business days.
3. **Step 3 - Final Administrative Appeal:** The employee may elevate the grievance to the Chief Executive Officer or an independent ombudsperson. The Step 3 determination is conclusive and represents the final administrative resolution within Acme Technologies.

### 15.3 Mutual Arbitration Agreement
Except where prohibited by applicable federal or state statute (such as claims concerning sexual harassment or sexual assault under the Ending Forced Arbitration of Sexual Assault and Sexual Harassment Act), all legal disputes arising out of the employment relationship, termination, or compensation that cannot be resolved through internal grievance procedures shall be resolved through binding bilateral arbitration administered by the American Arbitration Association (AAA) pursuant to its Employment Arbitration Rules.

---

## Section 16: Post-Employment Obligations, Non-Solicitation & Offboarding

### 16.1 Employee Offboarding and Exit Interview
When an employment separation date is finalized:
- **Exit Interview:** People Operations conducts a formal exit interview to collect feedback on company culture, managerial effectiveness, and operational bottlenecks. Participation is optional but strongly encouraged.
- **Access Revocation:** IT system credentials, Google Workspace access, Slack channels, and code repositories will be systematically deactivated at 5:00 PM EST on the employee's final working day (or immediately upon notice for garden leave).
- **Physical Property Handover:** As mandated in Section 9.4, all company-provided laptops, monitors, YubiKeys, corporate credit cards, and office badges must be surrendered within forty-eight (48) hours. Prepaid return shipping containers will be dispatched to remote employees.

### 16.2 Non-Solicitation and Restrictive Covenants
To protect Acme's proprietary goodwill, customer stability, and organizational workforce:
1. **Non-Solicitation of Employees:** For a period of **twelve (12) consecutive months** following separation of employment for any reason, former employees shall not directly or indirectly recruit, solicit, induce, or encourage any active Acme employee or contractor to terminate their relationship with Acme.
2. **Non-Solicitation of Clients:** For a period of **twelve (12) consecutive months** post-separation, former employees shall not solicit, divert, or attempt to divert any active client or customer with whom the former employee had substantial business interaction during the preceding twelve (12) months of their employment.
3. **Enforceability:** If any provision of this restrictive covenant is deemed overly broad by a court of competent jurisdiction, the clause shall be reformed to the maximum duration and scope permitted under applicable law.

### 16.3 Employment References and Verification
Acme maintains a neutral, standardized employment reference policy:
- Managers and colleagues are strictly prohibited from providing official written reference letters or character testimonials on company letterhead.
- All inquiries from prospective employers, mortgage lenders, or background check investigators must be directed to People Operations at `verifications@acme-tech.internal` or via The Work Number.
- Acme will disclose only the following objective factual data: employee full name, job title, initial start date, and separation date. Salary figures will only be confirmed with explicit written authorization from the employee.

---

## Section 17: Policy Revisions, Annual Recertification & Receipt Acknowledgment

### 17.1 Right to Amend Policies
Acme Technologies reserves the unilateral authority to modify, revise, supplement, or rescind any policy, benefit, or procedure outlined in this handbook at its sole discretion, with or without prior notice, provided such changes comply with governing federal, state, and local statutes. The Company will make reasonable commercial efforts to announce material policy revisions with at least thirty (30) days advance notice via email and all-hands communications.

### 17.2 Annual Recertification Requirement
Every active employee must recertify their understanding and acceptance of the Employee Handbook annually during the Q1 compliance window. Recertification is conducted electronically via the HR portal and requires completing the interactive compliance training module.

### 17.3 Document Revision History Log

| Version | Publication Date | Key Amendments / Modifications | Authorizing Executive |
| :--- | :--- | :--- | :--- |
| **V1.0** | January 15, 2021 | Initial handbook release and corporate baseline policies | CPO & General Counsel |
| **V2.0** | March 1, 2022 | Hybrid work guidelines, remote equipment stipends added | CPO & CEO |
| **V3.0** | January 10, 2024 | Enhanced parental leave (16 wks), 401(k) vesting changes | Chief People Officer |
| **V4.0** | January 5, 2025 | AI tooling acceptable use, PUMP Act lactation compliance | Chief Legal Officer |
| **V4.2** | January 1, 2026 | Travel per diem adjustments, emergency protocol refresh | Chief Executive Officer |

---

## Section 18: Employee Acknowledgment and Receipt

I hereby acknowledge that I have received, read, and understand the contents of the Acme Technologies Global HR Policies and Employee Handbook (2026 Edition, Reference ACME-HR-2026-V4.2).

I recognize that this handbook outlines the general operating policies and practices of the Company, and I agree to conform to all guidelines, ethical standards, and rules set forth herein. I understand that my employment with Acme Technologies Inc. is strictly at-will, meaning that either I or the Company may terminate the employment relationship at any time, with or without cause, subject to notice periods specified in Section 9.

I further understand that no manager, supervisor, or representative of Acme Technologies, other than the Chief Executive Officer in a signed written contract, possesses the authority to enter into any agreement for employment for any specified period of time, or to make any agreement contrary to the at-will policy.

**Employee Full Legal Name:** ________________________________________________  
**Employee Signature:** _______________________________________________________  
**Date:** ____________________________________________________________________  
**Employee ID Number:** ______________________________________________________  
"""


def parse_markdown_blocks(text: str):
    """Parses markdown text into structured blocks (headers, paragraphs, tables, lists)."""
    lines = text.split("\n")
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip()
        if not line or line == "---":
            i += 1
            continue

        if line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
            i += 1
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            i += 1
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            i += 1
        elif line.startswith("#### "):
            blocks.append(("h4", line[5:].strip()))
            i += 1
        elif line.startswith("|") and line.endswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                t_line = lines[i].strip()
                if not re.match(r"^\|(\s*:?-+:?\s*\|)+$", t_line):
                    cells = [c.strip() for c in t_line.split("|")[1:-1]]
                    table_lines.append(cells)
                i += 1
            if table_lines:
                blocks.append(("table", table_lines))
        elif line.startswith("- ") or line.startswith("* "):
            bullet_items = []
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                bullet_items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(("bullet_list", bullet_items))
        elif re.match(r"^\d+\.\s+", line):
            num_items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                m = re.match(r"^\d+\.\s+(.*)$", lines[i].strip())
                num_items.append(m.group(1).strip())
                i += 1
            blocks.append(("num_list", num_items))
        else:
            para_lines = [line]
            i += 1
            while (
                i < n
                and lines[i].strip()
                and not lines[i].startswith("#")
                and not (lines[i].strip().startswith("|") and lines[i].strip().endswith("|"))
                and not lines[i].strip().startswith("- ")
                and not re.match(r"^\d+\.\s+", lines[i].strip())
                and lines[i].strip() != "---"
            ):
                para_lines.append(lines[i].strip())
                i += 1
            blocks.append(("para", " ".join(para_lines)))
    return blocks


def clean_markdown_inline(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text


def build_pdf(blocks, output_path: Path):
    """Builds formatted PDF document using ReportLab."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=16,
        spaceAfter=6,
        keepWithNext=True
    )
    h3_style = ParagraphStyle(
        'DocH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    h4_style = ParagraphStyle(
        'DocH4',
        parent=styles['Heading4'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=7
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569")
    )

    story = []

    for b_type, content in blocks:
        if b_type == "h1":
            story.append(Paragraph(content, title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=12))
        elif b_type == "h2":
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
            story.append(Paragraph(content, h2_style))
        elif b_type == "h3":
            story.append(Paragraph(content, h3_style))
        elif b_type == "h4":
            story.append(Paragraph(content, h4_style))
        elif b_type == "para":
            p_text = content
            p_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", p_text)
            p_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", p_text)
            p_text = re.sub(r"`(.*?)`", r"<font face='Courier'>\1</font>", p_text)
            if "Document Reference:" in content or "Effective Date:" in content:
                story.append(Paragraph(p_text, meta_style))
            else:
                story.append(Paragraph(p_text, body_style))
        elif b_type == "bullet_list":
            for item in content:
                item_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", item)
                item_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", item_text)
                item_text = re.sub(r"`(.*?)`", r"<font face='Courier'>\1</font>", item_text)
                story.append(Paragraph(f"&bull; {item_text}", bullet_style))
            story.append(Spacer(1, 4))
        elif b_type == "num_list":
            for idx, item in enumerate(content, start=1):
                item_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", item)
                item_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", item_text)
                item_text = re.sub(r"`(.*?)`", r"<font face='Courier'>\1</font>", item_text)
                story.append(Paragraph(f"{idx}. {item_text}", bullet_style))
            story.append(Spacer(1, 4))
        elif b_type == "table":
            if not content:
                continue
            table_data = []
            for r_idx, row in enumerate(content):
                row_cells = []
                for cell in row:
                    c_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", cell)
                    c_style = ParagraphStyle(
                        f'Cell_{r_idx}',
                        parent=body_style,
                        fontSize=7.5,
                        leading=10,
                        textColor=colors.HexColor("#0F172A") if r_idx > 0 else colors.HexColor("#FFFFFF")
                    )
                    row_cells.append(Paragraph(c_text, c_style))
                table_data.append(row_cells)

            col_width = (letter[0] - 108) / len(content[0])
            t = Table(table_data, colWidths=[col_width] * len(content[0]))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated PDF: {output_path}")


def main():
    print("[1/2] Writing Markdown HR Policy to data/acme_corp_hr_policy.md...")
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(HANDBOOK_MD)
    print(f"[OK] Markdown written ({len(HANDBOOK_MD)} characters).")

    print("[2/2] Parsing blocks and building PDF via ReportLab...")
    blocks = parse_markdown_blocks(HANDBOOK_MD)
    build_pdf(blocks, PDF_FILE)


if __name__ == "__main__":
    main()

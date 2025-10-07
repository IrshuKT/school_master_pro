# School Master Pro (`student_master_pro`)

## Overview

**School Master Pro** is an Odoo module designed for comprehensive student management in educational institutions. It includes features for managing students, teachers, courses, exams, documents, and financial operations (fees, receipts, ledgers).

---

## Key Features

- **Student Management:** Track admission details, personal info, academic records, fee invoices, payments, documents, and transportation.
- **Teacher Management:** Assign teachers to students and courses.
- **Course Management:** Organize courses and academic years, manage course fees.
- **Exam Management:** Record exam results and grades.
- **Document Management:** Track student document collections and pending documents.
- **Fee & Accounts:** Automated invoice generation, concession handling, receipts, balance computation, ledgers.
- **Auto-Promotion:** Promote students to next year with carry-forward balances and fee automation.

---

## Models & Fields

### Student Master (`student.master`)
- Admission number, name, gender, date of birth, age (auto-computed)
- Guardian, address, contact info, Aadhaar details (with validation)
- Linked to teacher, course, year, invoices, receipts, exams, documents
- Fee computation, payment actions, concession wizard, auto-promotion logic

### Related Models
- `teacher.master`, `student.class.name`, `course.year.line`, `exam.result`, `student.fee.invoice`, `student.fee.receipt`, `student.documents.collection`, etc.

---

## User Interface

### Main Menus

- **SCHOOL MASTER PRO**
  - **Students Master**
    - Students Master (Kanban/List/Form)
  - **Teachers Master**
  - **Course**
    - Course, Subject
  - **Exam Master**
  - **Documents**
  - **Accounts**
    - Student Receipt, Receipt/Payment, Invoices, Student Ledger
  - **Ledgers**
    - Ledger Head, Cash Book, Bank Book

### Views

- **Kanban View:** Group students by year, display student info and photo cards
- **List View:** Responsive list of students with key details
- **Form View:** Full student profile, including personal, academic, fee, exam, and document info; includes action buttons (Save, Edit, Go Back, Pay Now, Apply Concession)

---

## How to Use

1. **Access the module** from the `SCHOOL MASTER PRO` menu.
2. **Create or view students** via the `Students Master` menu (Kanban/List/Form).
3. **Assign teachers, courses, and years** to students.
4. **Record fees, payments, and concessions** as needed.
5. **Promote students** to next year using the auto-promotion feature after academic year end.
6. **Track exam results, documents, and financial records** via respective menus.

---

## Developer Notes

- Models use Odoo ORM: validations, computed fields, constraints, and actions.
- Menu structure defined in XML for easy navigation.
- Invoices, receipts, and balances are automatically handled via model logic.
- Custom actions: save, edit, pay now, promote, concession wizard.
- Aadharr field validation ensures correct format (12 digits).

---

## Installation

1. Place the `school_master_pro` module in your Odoo `addons` directory.
2. Update the app list and install from Odoo Apps.
3. Configure courses, teachers, and other master data as needed.

---

## Screenshots

*(Include screenshots of Kanban, List, and Form views here for better understanding.)*

---

## Future Enhancements

- Complete remaining features (current progress: 80/100).
- Add more reporting and analytics.
- Improve mobile responsiveness.
- Integrate with other school systems (attendance, timetable).

---

## License

Specify your module’s license here (e.g., LGPL, AGPL, custom).

---

## Contact

For queries, contact the developer: [IrshuKT](https://github.com/IrshuKT) or refer to your organization’s support.

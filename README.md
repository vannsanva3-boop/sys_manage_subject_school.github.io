# Student Attendance Management System

ប្រព័ន្ធនេះប្រើ Flask និង SQLite។ វាគ្រប់គ្រងតែថ្នាក់ សិស្ស ការកត់ត្រាវត្តមានប្រចាំថ្ងៃ និងប្រវត្តិវត្តមាន។ Database file ត្រូវបានបង្កើតដោយស្វ័យប្រវត្តិនៅ `database/attendance.db` ហើយទិន្នន័យនៅសល់ក្រោយបិទ/បើកកម្មវិធីម្ដងទៀត។

## តម្រូវការ

- Python 3.10 ឬថ្មីជាងនេះ
- Visual Studio Code និង Python extension (ជាជម្រើស)

មិនត្រូវការដំឡើង SQL Server ឬ `pyodbc` ទេ។

## ដំឡើង និងបើកកម្មវិធី

បើក PowerShell ក្នុង folder project រួចដំណើរការ៖

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

បន្ទាប់មកចូលទៅ `http://127.0.0.1:5000`។ កម្មវិធីបង្កើតតារាងក្នុង `database/attendance.db` ដោយស្វ័យប្រវត្តិនៅពេលចាប់ផ្តើមលើកដំបូង។

បើ PowerShell រារាំងការបើក virtual environment សូមប្រើ៖

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## របៀបប្រើ

1. បង្កើតថ្នាក់នៅ **Classes**។
2. បន្ថែមសិស្សនៅ **Students** ហើយជ្រើសថ្នាក់។
3. នៅ **Attendance** ជ្រើសថ្នាក់ និងកាលបរិច្ឆេទ រួចជ្រើស `Present`, `Permission` ឬ `Absent` សម្រាប់សិស្សគ្រប់រូប មុនចុច Save។ អាចកែវត្តមានថ្ងៃចាស់បាន។
4. នៅ **History** ស្វែងរកតាមថ្ងៃ ថ្នាក់ ឈ្មោះ ឬ student code។

Class ដែលមានសិស្សមិនអាចលុបបាន។ Student ដែលមាន attendance history ក៏មិនអាចលុបបាន ដើម្បីរក្សាប្រវត្តិឱ្យបានត្រឹមត្រូវ។

## ឯកសារសំខាន់ៗ

- `app.py`: Flask entry point និង initialization របស់ database
- `database.py`: SQLite connection និង transaction helpers
- `database/schema.sql`: តារាង Classes, Students និង Attendance ព្រមទាំង constraints/indexes
- `routes/`: routes សម្រាប់គ្រប់មុខងារ
- `templates/`, `static/`: HTML, CSS និង JavaScript
- `database/attendance.db`: ទិន្នន័យដែលរក្សាទុកជាក់ស្តែង (បង្កើតពេលបើកកម្មវិធីលើកដំបូង)

កុំលុប `database/attendance.db` ប្រសិនបើចង់រក្សាទិន្នន័យ។ `database/schema.sql` ប្រើ `CREATE IF NOT EXISTS` ដូច្នេះការចាប់ផ្តើម app ម្តងទៀតមិនលុបទិន្នន័យទេ។

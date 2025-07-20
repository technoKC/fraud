@echo off
echo Setting up FraudShield...

echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

mkdir data 2>nul
mkdir reports 2>nul

echo Backend setup complete!

echo Setting up frontend...
cd ..\frontend
npm install

echo Frontend setup complete!

echo Setup finished! To run the application:
echo 1. Start backend: cd backend && python main.py
echo 2. Start frontend: cd frontend && npm start
pause
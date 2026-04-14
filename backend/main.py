import sys
import threading
import uvicorn
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PyQt5.QtWidgets import QApplication
from kiwoom_api import MockKiwoomAPI # 가상 API 사용
from strategy import TradingStrategy
from risk_manager import RiskManager
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("Main")

app = FastAPI(title="Mock Trading System")

# CORS (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 인스턴스
api_manager = None
strategy = None
risk_manager = None
trading_active = False

@app.get("/status")
async def get_status():
    return {
        "trading_active": trading_active,
        "market_status": risk_manager.market_status if risk_manager else "NORMAL",
        "holding_count": len(strategy.holding_stocks) if strategy else 0,
        "is_mock": True
    }

@app.post("/login")
async def login():
    if api_manager:
        api_manager.comm_connect()
        return {"message": "Mock Login Success"}
    return {"message": "API Not Initialized"}

@app.post("/start")
async def start_trading():
    global trading_active
    trading_active = True
    logger.info("가상 자동매매 시작!")
    return {"message": "Trading Started"}

@app.post("/stop")
async def stop_trading():
    global trading_active
    trading_active = False
    logger.info("가상 자동매매 중지")
    return {"message": "Trading Stopped"}

def real_data_handler(code, real_type, data):
    """지연 시간 최소화를 위한 매매 로직 (가상 데이터 대응)"""
    global trading_active, strategy, risk_manager
    if not trading_active:
        return
        
    # 가상 데이터 파싱 (price|bid_volume|volume)
    parts = data.split('|')
    current_price = int(parts[0])
    bid_volume = int(parts[1])
    
    # [10배 허매수 판별 로직 검증] - 평균 8,000주 대비 80,000주 이상 시 제외
    if strategy.is_spoofing(code, bid_volume, 8000):
        return

    # [매수/매칭 로직 호출 등의 시뮬레이션]
    # 실제 strategy.check_entry_signal() 등을 호출하여 로그 출력

def run_qt_loop():
    global api_manager, strategy, risk_manager
    qt_app = QApplication(sys.argv)
    
    api_manager = MockKiwoomAPI()
    strategy = TradingStrategy(api_manager)
    risk_manager = RiskManager(api_manager)
    
    # 가상 데이터 핸들러 연결
    api_manager.callback = real_data_handler
    
    logger.info("가상 자동매매 서버(Mock) 초기화 완료.")
    sys.exit(qt_app.exec_())

if __name__ == "__main__":
    # FastAPI 서버 스레드
    server_thread = threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
    server_thread.daemon = True
    server_thread.start()
    
    # 메인 스레드에서 Qt 루프 실행
    run_qt_loop()

import logging
import random
import time
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

logger = logging.getLogger("MockKiwoomAPI")

class MockKiwoomAPI(QObject):
    # 실제 API와 동일한 시그널 모사
    OnEventConnect = pyqtSignal(int)
    OnReceiveRealData = pyqtSignal(str, str, str)
    
    def __init__(self):
        super().__init__()
        self.callback = None
        self.is_connected = False
        
        # 가상 데이터 생성을 위한 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self._generate_mock_data)

    def comm_connect(self):
        """가상 로그인 처리"""
        logger.info("가상 모드: 키움 서버 연결 시도 중...")
        time.sleep(1)
        self.is_connected = True
        logger.info("가상 모드: 연결 성공 (Mock Mode Active)")
        self.OnEventConnect.emit(0)
        self.timer.start(1000) # 1초마다 데이터 생성

    def get_login_info(self, tag):
        """가상 사용자 정보"""
        mock_info = {
            "ACCOUNT_CNT": "1",
            "ACCLIST": "8123456789",
            "USER_ID": "mock_user",
            "USER_NAME": "가상사용자"
        }
        return mock_info.get(tag, "")

    def _generate_mock_data(self):
        """실시간 주가 흐름 시뮬레이션 (10배 허매수 조건 포함)"""
        code = "005930" # 삼성전자 모사
        current_price = random.randint(70000, 75000)
        
        # 가끔 허매수(10배 물량) 발생 시뮬레이션
        is_fake_order = random.random() < 0.2
        bid_volume = 100000 if is_fake_order else 5000
        
        mock_real_data = f"{current_price}|{bid_volume}|{random.randint(100, 500)}"
        
        if self.callback:
            self.callback(code, "주식체결", mock_real_data)

    def send_order(self, rq_name, screen_no, acc_no, order_type, code, qty, price, hoga_type, origin_order_no):
        """가상 주문 처리"""
        logger.info(f"[가상주문] {code} {qty}주 {order_type} 접수 완료")
        return 0

    def get_comm_data(self, tr_code, record_name, index, item_name):
        return "0"

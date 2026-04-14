import logging
import time

logger = logging.getLogger("RiskManager")

class RiskManager:
    def __init__(self, api_manager):
        self.api = api_manager
        self.last_index_check_time = 0
        self.market_status = "NORMAL" # NORMAL, CAUTION, STOP
        self.INDEX_CHECK_INTERVAL = 180 # 3분 (180초)
        
    def check_market_condition(self, kospi_index, kosdaq_index):
        """
        [4. 리스크 관리 및 자금 운용 - 하락장 비중 축소]
        지수가 주요 이평선(20일선 등)을 깨거나 폭락 시 비중 절감
        """
        current_time = time.time()
        if current_time - self.last_index_check_time < self.INDEX_CHECK_INTERVAL:
            return self.market_status
            
        # [지수 데이터 체크] - 3분 단위로 로직 실행
        if kospi_index['change_rate'] < -0.02 or kosdaq_index['change_rate'] < -0.03:
            logger.warning(f"시장 급락 감지 (KOSPI {kospi_index['change_rate']}%). 하락장 비중 축소 모드로 전환.")
            self.market_status = "CAUTION"
        elif kospi_index['current'] < kospi_index['ma20'] or kosdaq_index['current'] < kosdaq_index['ma20']:
            logger.warning("지수가 20일선을 하회함. 관망 모드로 전환.")
            self.market_status = "STOP"
        else:
            self.market_status = "NORMAL"
            
        self.last_index_check_time = current_time
        return self.market_status

    def can_order(self, code, current_price, holding_stocks, order_type="BUY"):
        """
        [물타기 절대 금지 / 불타기 허용]
        """
        if order_type == "BUY":
            stock_info = holding_stocks.get(code)
            
            # 1. 물타기 금지: 이미 보유 중인데 손실 중이면 추가 매수 불가
            if stock_info and current_price < stock_info['buy_price']:
                logger.error(f"[{code}] 물타기 시도 감지! 추가 매수 금지.")
                return False
                
            # 2. 불타기 허용: 이미 보유 중인데 수익 중이며 주력이 돌파될 때만 가능
            if stock_info and current_price > stock_info['buy_price'] * 1.01:
                 logger.info(f"[{code}] 수익 중 추가 매수(불타기) 조건 충족.")
                 return True
                 
            # 3. 신규 진입 시 시장 상태에 따른 비중 조절
            if self.market_status == "STOP":
                 logger.info("시장 하락장으로 인한 신규 진입 차단.")
                 return False
                 
        return True

    def get_order_qty(self, code, current_price, balance):
        """
        자금 관리: 시장 상태에 따른 베팅 금액 조절
        """
        base_bet_amount = balance * 0.1 # 기본 10% 비중
        
        if self.market_status == "CAUTION":
            base_bet_amount *= 0.5 # 하락장에서는 5%로 축소
            
        qty = int(base_bet_amount / current_price)
        return qty

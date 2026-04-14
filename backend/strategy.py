import logging
import datetime

logger = logging.getLogger("Strategy")

class TradingStrategy:
    def __init__(self, api_manager):
        self.api = api_manager
        self.target_codes = [] # 감시설정 종목 리스트
        self.holding_stocks = {} # 현재 보유 종목 정보 {code: {buy_price, qty, ...}}
        
        # [설정값 반영]
        self.FAKE_ORDER_THRESHOLD = 10 # 평균 거래량 대비 10배 허매수 판별
        self.BREAKEVEN_BUFFER = 0.003 # 수수료 및 세금 포함 약 0.3% 버퍼

    def filter_universe(self, market_data):
        """
        [1. 종목 선정 조건 (Target Universe)]
        거래대금 및 거래량 상위 종목 중 전고점 돌파 가능성이 높은 종목 선정
        """
        filtered = []
        for stock in market_data:
            # 거래대금 상위 조건 확인 (API에서 받은 데이터 기반)
            if stock['trading_value'] < 100000000: # 예: 1억 미만 제외
                continue
                
            # 전고점 근처 여부 (현재가 > 전고점 * 0.98)
            if stock['current_price'] < stock['high_52week'] * 0.98:
                continue
                
            filtered.append(stock['code'])
        
        self.target_codes = filtered
        logger.info(f"대상 종목 선정 완료: {len(self.target_codes)}개")

    def is_spoofing(self, code, current_bid_volume, avg_volume):
        """
        [블랙리스트 제외 로직]
        호가창에 평균 대비 비정상적으로 큰 대기 물량(허매수)이 있는지 판별
        """
        if avg_volume > 0 and current_bid_volume > avg_volume * self.FAKE_ORDER_THRESHOLD:
            logger.warning(f"[{code}] 허매수 감지! (현재 매수잔량: {current_bid_volume}, 평균: {avg_volume}) -> 매매 제외")
            return True
        return False

    def check_entry_signal(self, code, price_info, order_book):
        """
        [2. 매수 진입 로직 (Entry Logic)]
        돌파 매수 및 눌림목 지지 확인
        """
        current_price = price_info['current']
        open_price = price_info['open']
        morning_high = price_info['morning_high'] # 9:30 이전 고점
        
        # [돌파 매수] 시초가 및 장 초반 고점 돌파 확인
        if current_price > open_price and current_price > morning_high:
            logger.info(f"[{code}] 전고점/시초가 돌파 시그널 발생 (가격: {current_price})")
            return "BREAKOUT"
            
        # [눌림목 매수] 하락 속도 감소 및 매수 대기 물량 확인
        if price_info['is_dropping'] and order_book['bid_depth'] > order_book['ask_depth'] * 2:
            logger.info(f"[{code}] 눌림목 지지 확인 (호가 잔량 우세)")
            return "PULLBACK"
            
        return None

    def check_exit_signal(self, code, current_price, elapsed_time):
        """
        [3. 매도 및 손절 로직 (Exit & Stop-loss) - 최우선 구현]
        지연 시간 최소화를 위한 즉각적인 반응 확인
        """
        stock_info = self.holding_stocks.get(code)
        if not stock_info:
            return None
            
        buy_price = stock_info['buy_price']
        profit_rate = (current_price - buy_price) / buy_price
        
        # 1. 즉각적인 반응 확인 (진입 후 일정 시간 내 상승 없을 시 즉시 매도)
        if elapsed_time > 60 and profit_rate < 0.005: 
            return {"type": "MARKET_SELL", "reason": "지체되는 상승 반응으로 인한 즉시 매도"}
            
        # 2. 본전 손절 (Breakeven Cut) - 수수료/세금 감안
        if profit_rate < 0 and current_price <= buy_price * (1 + self.BREAKEVEN_BUFFER):
             return {"type": "MARKET_SELL", "reason": "본전 위협으로 인한 기계적 손절"}
             
        # 3. 짧은 수익 실현 (1~2% 익절)
        if profit_rate >= 0.015:
             return {"type": "MARKET_SELL", "reason": "목표 수익 도달 (1.5% 이상)"}
             
        return None

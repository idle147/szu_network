import sys
import requests
import time
import os
import wmi
import yaml

from typing import List
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from loguru import logger


class ConnectionError(Exception):
    """网络连接错误"""

    def __init__(self, message: str = "网络连接失败"):
        super().__init__(message)


@dataclass
class NetworkConfig:
    username: str
    password: str
    url: str = "https://net.szu.edu.cn"
    check_interval: int = 30
    connection_timeout: int = 2
    test_urls: List[str] = None

    def __post_init__(self):
        if self.test_urls is None:
            self.test_urls = ["https://www.baidu.com", "https://www.qq.com"]


class NetworkConnector:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.wmi_obj = wmi.WMI()
        self._setup_logging()

    def _setup_logging(self):
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO",
            colorize=True,
        )
        # 输出到文件
        logger.add(
            "logs/szu_connect_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            rotation="00:00",  # 每天轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            encoding="utf-8",
            level="INFO",
        )

    def _load_config(self, config_path: str) -> NetworkConfig:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = {"username": "your_username", "password": "your_password"}
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
        return NetworkConfig(**config_data)

    def _get_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        # Selenium 4.6.0+ 会自动下载和管理驱动
        return webdriver.Chrome(options=chrome_options)

    def check_cable_connected(self, max_retries: int = 3) -> bool:
        """检查网络电缆是否物理连接

        Args:
            max_retries: 最大重试次数,默认3次

        Returns:
            bool: True表示有线网络已连接,False表示未连接
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                nics = self.wmi_obj.Win32_NetworkAdapter(PhysicalAdapter=True, NetConnectionStatus=2)  # 直接筛选已连接状态
                for nic in nics:
                    # 检查是否是有线网卡且处于工作状态
                    if (
                        "802.3" in nic.AdapterType
                        and nic.NetEnabled
                        and not nic.NetConnectionID.startswith("VMware")
                        and not nic.NetConnectionID.startswith("VirtualBox")
                    ):
                        return True
                return False

            except wmi.x_wmi as e:
                retry_count += 1
                logger.warning(f"WMI连接异常,重试{retry_count}/{max_retries}: {str(e)}")
                if retry_count < max_retries:
                    self.wmi_obj = wmi.WMI()
                    time.sleep(1)  # 重试前等待
                continue

            except Exception as e:
                ConnectionError(e)

        logger.error("达到最大重试次数,网络检查失败")
        return False

    def check_connection(self) -> bool:
        if self.check_cable_connected() is False:
            return False
        for url in self.config.test_urls:
            try:
                response = requests.head(url, timeout=self.config.connection_timeout)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                return False
        return False

    def do_connect(self, time_wait=0.5) -> bool:
        driver = self._get_driver()
        try:
            driver.get(self.config.url)
            wait = WebDriverWait(driver, time_wait)

            # 检查是否出现logout按钮, 如果有则表示已经登录, 直接返回
            try:
                wait.until(EC.presence_of_element_located((By.ID, "logout")))
                logger.info("已登录,无需重新连接")
                return True
            except TimeoutException:
                pass  # 未找到logout按钮,继续登录流程

            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            login_button = wait.until(EC.presence_of_element_located((By.ID, "login-account")))

            username_field.send_keys(self.config.username)
            password_field.send_keys(self.config.password)
            login_button.click()

            # 检查是否出现弹窗
            try:
                dialog = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content > div.section")))
                raise ConnectionError(dialog.text)

            except TimeoutException:
                return bool(wait.until(EC.presence_of_element_located((By.ID, "logout"))))
        finally:
            driver.quit()

    def run(self):
        logger.info("启动网络连接监控...")
        while True:
            try:
                if not self.check_connection():
                    logger.warning("发现网络连接断开")
                    if self.do_connect():
                        logger.info("重新连接成功")
                    else:
                        logger.error("重新连接失败")
                else:
                    logger.info("网络连接正常")
                logger.info(f"沉睡{self.config.check_interval}秒, 等待下一次检查...")
                time.sleep(self.config.check_interval)
            except ConnectionError as e:
                logger.error(f"连接异常: {str(e)}")
                break


if __name__ == "__main__":
    connector = NetworkConnector()
    try:
        connector.run()
    except Exception as e:
        import traceback

        stack_trace = traceback.format_exc()
        logger.error(f"程序异常: {str(e)}\n堆栈跟踪:\n{stack_trace}")

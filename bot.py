import requests
import json
import os
import time
from datetime import datetime
import urllib3
import threading
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 版权
def show_copyright():
    """展示版权信息"""
    copyright_info = f"""{Fore.CYAN}
    *****************************************************
    *           X:https://x.com/ariel_sands_dan         *
    *           Tg:https://t.me/sands0x1                *
    *           Copyright (c) 2025                      *
    *           All Rights Reserved                     *
    *****************************************************
    """
    {Style.RESET_ALL}
    print(copyright_info)
    print('=' * 50)
    print(f"{Fore.GREEN}申请key: https://661100.xyz/ {Style.RESET_ALL}")
    print(f"{Fore.RED}联系Dandan: \n QQ:712987787 QQ群:1036105927 \n 电报:sands0x1 电报群:https://t.me/+fjDjBiKrzOw2NmJl \n 微信: dandan0x1{Style.RESET_ALL}")
    print('=' * 50)

# ANSI颜色代码
class Colors:
    # 基础颜色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # 背景颜色
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'

    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

    # 重置
    RESET = '\033[0m'

    @staticmethod
    def colorize(text, color):
        """给文本添加颜色"""
        return f"{color}{text}{Colors.RESET}"

class PointClaimCLI:
    def __init__(self):
        # 彩色启动界面
        title = "🎯 Add+ 自动涨分工具 (多账户并发版)"
        subtitle1 = "✨ 智能获取用户名并自动增长积分"
        subtitle2 = "🚀 支持多账户并发处理，效率翻倍"
        print(Colors.colorize(Colors.colorize(title, Colors.BOLD + Colors.YELLOW).center(0) , Colors.CYAN))
        print(Colors.colorize(Colors.colorize(subtitle1, Colors.GREEN).center(0), Colors.CYAN))
        print(Colors.colorize(Colors.colorize(subtitle2, Colors.BLUE).center(0), Colors.CYAN))
        print()

        # 控制变量
        self.is_running = False
        self.client_username_file = "config/x_name.json"
        self.cookie_file = "config/cookie.txt"
        self.processed_count = 0
        self.lock = threading.Lock()  # 用于线程安全的日志输出

    def log_message(self, message, msg_type="info"):
        """添加彩色日志消息（线程安全）"""
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")

            # 根据消息类型选择颜色和emoji
            if msg_type == "success":
                colored_msg = Colors.colorize(f"✅ {message}", Colors.GREEN)
            elif msg_type == "error":
                colored_msg = Colors.colorize(f"❌ {message}", Colors.RED)
            elif msg_type == "warning":
                colored_msg = Colors.colorize(f"⚠️  {message}", Colors.YELLOW)
            elif msg_type == "info":
                colored_msg = Colors.colorize(f"ℹ️  {message}", Colors.BLUE)
            elif msg_type == "processing":
                colored_msg = Colors.colorize(f"⚙️  {message}", Colors.CYAN)
            elif msg_type == "account":
                colored_msg = Colors.colorize(f"👤 {message}", Colors.MAGENTA)
            else:
                colored_msg = message

            timestamp_colored = Colors.colorize(f"[{timestamp}]", Colors.DIM + Colors.WHITE)
            log_entry = f"{timestamp_colored} {colored_msg}"
            print(log_entry)

    def update_status(self, status_text, status_type="info"):
        """更新彩色状态显示"""
        with self.lock:
            if status_type == "success":
                status_colored = Colors.colorize(status_text, Colors.GREEN + Colors.BOLD)
                emoji = "🎉"
            elif status_type == "error":
                status_colored = Colors.colorize(status_text, Colors.RED + Colors.BOLD)
                emoji = "💥"
            elif status_type == "warning":
                status_colored = Colors.colorize(status_text, Colors.YELLOW + Colors.BOLD)
                emoji = "⚠️"
            elif status_type == "processing":
                status_colored = Colors.colorize(status_text, Colors.CYAN + Colors.BOLD)
                emoji = "⚙️"
            else:
                status_colored = Colors.colorize(status_text, Colors.BLUE + Colors.BOLD)
                emoji = "📊"

            print(f"{emoji} {Colors.colorize('状态：', Colors.WHITE + Colors.BOLD)}{status_colored}")

    def update_count(self, count, count_type="info"):
        """更新彩色处理数量显示"""
        with self.lock:
            self.processed_count = count
            count_colored = Colors.colorize(str(count), Colors.GREEN + Colors.BOLD)
            print(f"📈 {Colors.colorize('处理数量：', Colors.WHITE + Colors.BOLD)}{count_colored}")

    def load_cookies_from_file(self):
        """从cookie.txt文件加载所有cookie"""
        try:
            if not os.path.exists(self.cookie_file):
                self.log_message(f"未找到 {self.cookie_file} 文件", "error")
                return []

            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = []
                for line_num, line in enumerate(f, 1):
                    cookie = line.strip()
                    if cookie and not cookie.startswith('#'):  # 忽略空行和注释行
                        cookies.append({
                            'cookie': cookie,
                            'account_id': f"账户{line_num}"
                        })

                if cookies:
                    self.log_message(f"成功加载 {Colors.colorize(str(len(cookies)), Colors.BOLD + Colors.GREEN)} 个Cookie账户", "success")
                else:
                    self.log_message("Cookie文件中没有找到有效的账户", "warning")
                return cookies

        except Exception as e:
            self.log_message(f"读取Cookie文件失败: {str(e)}", "error")
            return []
    
    def get_usernames_from_api(self):
        """从API获取用户名数据"""
        try:
            self.log_message("正在从API获取用户名数据...", "processing")
            response = requests.get("http://81.70.150.62:3000/api/usernames", timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                usernames = data.get("data", [])
                count_colored = Colors.colorize(str(len(usernames)), Colors.BOLD + Colors.GREEN)
                self.log_message(f"成功获取到 {count_colored} 个用户名", "success")
                return usernames
            else:
                self.log_message("API返回失败状态", "error")
                return []
        except requests.exceptions.RequestException as e:
            self.log_message(f"API请求失败: {str(e)}", "error")
            return []
        except Exception as e:
            self.log_message(f"获取用户名数据时出错: {str(e)}", "error")
            return []
    
    def load_client_username_file(self):
        """加载client_username.json文件"""
        try:
            if os.path.exists(self.client_username_file):
                with open(self.client_username_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            else:
                return []
        except Exception as e:
            self.log_message(f"加载client_username文件失败: {str(e)}")
            return []
    
    def save_client_username_file(self, data):
        """保存数据到client_username.json文件"""
        try:
            with open(self.client_username_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            count_colored = Colors.colorize(str(len(data)), Colors.BOLD + Colors.GREEN)
            file_colored = Colors.colorize(self.client_username_file, Colors.BOLD + Colors.CYAN)
            self.log_message(f"已保存 {count_colored} 个用户名到 {file_colored}", "success")
            return True
        except Exception as e:
            self.log_message(f"保存client_username文件失败: {str(e)}", "error")
            return False
    
    def update_client_username_data(self, api_usernames):
        """更新client_username数据"""
        # 加载现有数据
        existing_data = self.load_client_username_file()
        
        # 获取当前最大编号
        max_number = 0
        if existing_data:
            max_number = max([item.get("number", 0) for item in existing_data])
        
        max_colored = Colors.colorize(str(max_number), Colors.BOLD + Colors.YELLOW)
        self.log_message(f"当前文件中最大编号: {max_colored}", "info")

        # 筛选出需要添加的新数据（编号大于当前最大编号）
        new_data = []
        for user in api_usernames:
            if user.get("number", 0) > max_number:
                new_data.append({
                    "number": user.get("number"),
                    "username": user.get("username")
                })

        if new_data:
            # 按编号排序
            new_data.sort(key=lambda x: x.get("number", 0))

            # 用新数据覆盖整个文件
            if self.save_client_username_file(new_data):
                count_colored = Colors.colorize(str(len(new_data)), Colors.BOLD + Colors.GREEN)
                self.log_message(f"发现 {count_colored} 个新用户名，已覆盖保存", "success")
                return new_data
        else:
            self.log_message("没有新的用户名数据需要添加", "warning")
            return []
        
        return []
    
    def send_claim_request(self, username, cookie, account_id=""):
        """发送涨分请求"""
        try:
            url = "https://addplus.org/api/trpc/users.claimPoints?batch=1"

            headers = {
                "Host": "addplus.org",
                "Connection": "keep-alive",
                "sec-ch-ua-platform": "\"Windows\"",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
                "trpc-accept": "application/jsonl",
                "content-type": "application/json",
                "x-trpc-source": "nextjs-react",
                "sec-ch-ua-mobile": "?0",
                "Accept": "*/*",
                "Origin": "https://addplus.org",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": f"https://addplus.org/boost/{username}",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cookie": cookie
            }

            payload = {
                "0": {
                    "json": {
                        "username": username
                    }
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)

            # 格式化账户和用户名显示
            if account_id:
                account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = f"{account_colored} {username_colored}"
            else:
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = username_colored

            if response.status_code == 200:
                self.log_message(f"{display_name} - 涨分成功", "success")
                return True
            else:
                status_colored = Colors.colorize(str(response.status_code), Colors.RED + Colors.BOLD)
                self.log_message(f"{display_name} - 涨分失败 (状态码: {status_colored})", "error")
                return False

        except requests.exceptions.RequestException as e:
            if account_id:
                account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = f"{account_colored} {username_colored}"
            else:
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = username_colored
            self.log_message(f"{display_name} - 网络请求失败: {str(e)}", "error")
            return False
        except Exception as e:
            if account_id:
                account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = f"{account_colored} {username_colored}"
            else:
                username_colored = Colors.colorize(username, Colors.CYAN + Colors.BOLD)
                display_name = username_colored
            self.log_message(f"{display_name} - 发送请求时出错: {str(e)}", "error")
            return False

    def process_single_account(self, cookie_info, client_data):
        """处理单个账户的涨分流程"""
        cookie = cookie_info['cookie']
        account_id = cookie_info['account_id']

        success_count = 0
        total_count = len(client_data)

        account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
        count_colored = Colors.colorize(str(total_count), Colors.BOLD + Colors.GREEN)
        self.log_message(f"{account_colored} 开始处理 {count_colored} 个用户名...", "account")

        for i, user_data in enumerate(client_data):
            if not self.is_running:
                self.log_message(f"{account_colored} 用户停止了处理流程", "warning")
                break

            username = user_data.get("username")
            number = user_data.get("number")

            if username:
                number_colored = Colors.colorize(f"#{number}", Colors.YELLOW + Colors.BOLD)
                username_colored = Colors.colorize(username, Colors.CYAN)
                progress_colored = Colors.colorize(f"({i+1}/{total_count})", Colors.DIM + Colors.WHITE)
                self.log_message(f"{account_colored} 正在处理 {number_colored} - {username_colored}... {progress_colored}", "processing")

                if self.send_claim_request(username, cookie, account_id):
                    success_count += 1

                # 添加延迟避免请求过快
                if self.is_running and i < total_count - 1:  # 不是最后一个
                    time.sleep(1)  # 减少延迟，因为多账户并发

        success_colored = Colors.colorize(str(success_count), Colors.GREEN + Colors.BOLD)
        total_colored = Colors.colorize(str(total_count), Colors.BLUE + Colors.BOLD)
        self.log_message(f"{account_colored} 处理完成！成功: {success_colored}/{total_colored}", "success")
        return success_count, total_count

    def claim_process_multi_account(self, cookies):
        """多账户并发涨分处理流程"""
        try:
            if not cookies:
                self.log_message("❌ 没有可用的Cookie账户")
                self.update_status("错误：缺少Cookie")
                return

            account_count_colored = Colors.colorize(str(len(cookies)), Colors.BOLD + Colors.MAGENTA)
            self.log_message(f"开始多账户并发涨分... (共{account_count_colored}个账户)", "account")
            self.update_status("正在获取数据", "processing")

            # 1. 从API获取用户名数据
            api_usernames = self.get_usernames_from_api()
            if not api_usernames:
                self.log_message("无法获取用户名数据，停止处理", "error")
                self.update_status("错误：无法获取数据", "error")
                return

            # 2. 更新client_username文件
            self.update_status("正在分析数据", "processing")
            client_data = self.update_client_username_data(api_usernames)
            if not client_data:
                self.log_message("没有可处理的用户名数据", "warning")
                self.update_status("完成：无新数据", "warning")
                return

            # 3. 使用线程池并发处理多个账户
            data_count_colored = Colors.colorize(str(len(client_data)), Colors.BOLD + Colors.GREEN)
            account_count_colored = Colors.colorize(str(len(cookies)), Colors.BOLD + Colors.MAGENTA)
            self.log_message(f"开始并发处理 {data_count_colored} 个用户名，使用 {account_count_colored} 个账户...", "processing")
            self.update_status(f"并发处理中 ({len(cookies)}个账户)", "processing")

            total_success = 0
            total_processed = 0

            with ThreadPoolExecutor(max_workers=len(cookies)) as executor:
                # 为每个cookie账户提交任务
                future_to_account = {
                    executor.submit(self.process_single_account, cookie_info, client_data): cookie_info['account_id']
                    for cookie_info in cookies
                }

                # 等待所有任务完成
                for future in as_completed(future_to_account):
                    account_id = future_to_account[future]
                    try:
                        success_count, total_count = future.result()
                        total_success += success_count
                        total_processed += total_count
                        account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
                        self.log_message(f"{account_colored} 任务完成", "success")
                    except Exception as e:
                        account_colored = Colors.colorize(f"[{account_id}]", Colors.MAGENTA + Colors.BOLD)
                        self.log_message(f"{account_colored} 处理出错: {str(e)}", "error")

            if self.is_running:
                success_colored = Colors.colorize(str(total_success), Colors.GREEN + Colors.BOLD)
                total_colored = Colors.colorize(str(total_processed), Colors.BLUE + Colors.BOLD)
                self.log_message(f"所有账户处理完成！总成功: {success_colored}/{total_colored}", "success")
                self.update_status(f"完成 ({total_success}/{total_processed} 成功)", "success")

        except Exception as e:
            self.log_message(f"多账户涨分流程出错: {str(e)}", "error")
            self.update_status("错误", "error")
        finally:
            self.is_running = False

    def claim_process(self, cookie):
        """涨分处理流程"""
        try:
            if not cookie:
                self.log_message("❌ 请先输入Cookie")
                self.update_status("错误：缺少Cookie")
                return

            self.log_message("开始单账户涨分...", "processing")
            self.update_status("正在获取数据", "processing")

            # 1. 从API获取用户名数据
            api_usernames = self.get_usernames_from_api()
            if not api_usernames:
                self.log_message("无法获取用户名数据，停止处理", "error")
                self.update_status("错误：无法获取数据", "error")
                return

            # 2. 更新client_username文件
            self.update_status("正在分析数据", "processing")
            client_data = self.update_client_username_data(api_usernames)
            if not client_data:
                self.log_message("没有可处理的用户名数据", "warning")
                self.update_status("完成：无新数据", "warning")
                return

            # 3. 依次发送涨分请求
            count_colored = Colors.colorize(str(len(client_data)), Colors.BOLD + Colors.GREEN)
            self.log_message(f"开始 {count_colored} 个涨分链接...", "processing")
            self.update_status(f"处理中 (0/{len(client_data)})", "processing")

            success_count = 0
            for i, user_data in enumerate(client_data):
                if not self.is_running:
                    self.log_message("用户停止了处理流程", "warning")
                    self.update_status("已停止", "warning")
                    break

                username = user_data.get("username")
                number = user_data.get("number")

                if username:
                    number_colored = Colors.colorize(f"#{number}", Colors.YELLOW + Colors.BOLD)
                    username_colored = Colors.colorize(username, Colors.CYAN)
                    progress_colored = Colors.colorize(f"({i+1}/{len(client_data)})", Colors.DIM + Colors.WHITE)
                    self.log_message(f"正在处理 {number_colored} - {username_colored}... {progress_colored}", "processing")
                    self.update_status(f"处理中 ({i+1}/{len(client_data)})", "processing")
                    self.update_count(i+1)

                    if self.send_claim_request(username, cookie):
                        success_count += 1

                    # 添加延迟避免请求过快
                    if self.is_running and i < len(client_data) - 1:  # 不是最后一个
                        time.sleep(2)

            if self.is_running:
                success_colored = Colors.colorize(str(success_count), Colors.GREEN + Colors.BOLD)
                total_colored = Colors.colorize(str(len(client_data)), Colors.BLUE + Colors.BOLD)
                self.log_message(f"涨分完成！成功: {success_colored}/{total_colored}", "success")
                self.update_status(f"完成 ({success_count}/{len(client_data)} 成功)", "success")

        except Exception as e:
            self.log_message(f"涨分流程出错: {str(e)}", "error")
            self.update_status("错误", "error")
        finally:
            self.is_running = False
    
    def start_claim_process(self, cookie=None):
        """启动涨分流程（单账户）"""
        if not self.is_running:
            if not cookie:
                print("❌ 警告：请先输入Cookie后再开始！")
                return

            self.is_running = True
            self.update_status("启动中")
            self.update_count(0)

            self.log_message("准备开始单账户涨分...", "info")

            # 直接运行涨分流程
            self.claim_process(cookie)

    def start_multi_account_process(self):
        """启动多账户并发涨分流程"""
        if not self.is_running:
            # 从文件加载所有cookie
            cookies = self.load_cookies_from_file()
            if not cookies:
                print(Colors.colorize("❌ 警告：未找到有效的Cookie账户！", Colors.RED + Colors.BOLD))
                return

            self.is_running = True
            self.update_status("启动中", "processing")
            self.update_count(0)

            account_count_colored = Colors.colorize(str(len(cookies)), Colors.BOLD + Colors.MAGENTA)
            self.log_message(f"准备开始多账户并发涨分... (共{account_count_colored}个账户)", "account")

            # 运行多账户并发涨分流程
            self.claim_process_multi_account(cookies)

    def stop_process(self):
        """停止处理流程"""
        if self.is_running:
            self.is_running = False
            self.log_message("正在停止处理流程...", "warning")
            self.update_status("正在停止", "warning")
        else:
            self.log_message("当前没有运行中的流程", "info")

def main():
    show_copyright()
    app = PointClaimCLI()

    # 彩色模式选择界面
    print(Colors.colorize(Colors.colorize("📋 请选择运行模式", Colors.BOLD + Colors.YELLOW).center(0), Colors.BLUE))
    print(Colors.colorize(Colors.colorize("1. 🔸 单账户模式 (手动输入Cookie)", Colors.GREEN).ljust(60), Colors.BLUE))
    print(Colors.colorize(Colors.colorize("2. 🔹 多账户并发模式 (从cookie.txt读取)", Colors.CYAN).ljust(60), Colors.BLUE))

    while True:
        choice_prompt = Colors.colorize("\n🎯 请输入选择 (1 或 2): ", Colors.BOLD + Colors.WHITE)
        choice = input(choice_prompt).strip()

        if choice == "1":
            # 单账户模式
            print(Colors.colorize(Colors.colorize("🍪 单账户模式", Colors.BOLD + Colors.YELLOW).center(58), Colors.GREEN))

            print(Colors.colorize("📝 请输入您的 AddPlus 网站 Cookie：", Colors.CYAN))
            print(Colors.colorize("💡 提示：从浏览器开发者工具中复制完整的Cookie字符串", Colors.DIM + Colors.WHITE))

            cookie_prompt = Colors.colorize("Cookie: ", Colors.BOLD + Colors.YELLOW)
            cookie = input(cookie_prompt).strip()

            if not cookie:
                print(Colors.colorize("❌ 错误：Cookie不能为空！", Colors.RED + Colors.BOLD))
                return

            print(Colors.colorize("\n🚀 开始执行单账户涨分流程...", Colors.GREEN + Colors.BOLD))
            app.start_claim_process(cookie)
            break

        elif choice == "2":
            # 多账户并发模式
            print(Colors.colorize( Colors.colorize("📁 多账户并发模式", Colors.BOLD + Colors.YELLOW).center(0), Colors.MAGENTA))

            print(Colors.colorize("📋 请确保 cookie.txt 文件存在，每行一个Cookie", Colors.CYAN))
            print(Colors.colorize("📄 格式示例：", Colors.WHITE + Colors.BOLD))
            print(Colors.colorize("  session_id=abc123; user_token=xyz789", Colors.DIM + Colors.GREEN))
            print(Colors.colorize("  session_id=def456; user_token=uvw012", Colors.DIM + Colors.GREEN))
            print(Colors.colorize("  # 这是注释行，会被忽略", Colors.DIM + Colors.YELLOW))

            confirm_prompt = Colors.colorize("\n✨ 确认开始多账户并发处理？(y/n): ", Colors.BOLD + Colors.CYAN)
            confirm = input(confirm_prompt).strip().lower()
            if confirm in ['y', 'yes', '是']:
                print(Colors.colorize("\n🚀 开始执行多账户并发涨分流程...", Colors.MAGENTA + Colors.BOLD))
                app.start_multi_account_process()
            else:
                print(Colors.colorize("❌ 已取消操作", Colors.YELLOW + Colors.BOLD))
            break

        else:
            print(Colors.colorize("❌ 无效选择，请输入 1 或 2", Colors.RED + Colors.BOLD))

if __name__ == "__main__":
    main()

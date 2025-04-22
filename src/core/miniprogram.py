import time
from typing import Optional
import uiautomator2 as u2
from utils.logger import Logger

class MiniProgram:
    def __init__(self, device: u2.Device, config: dict, logger: Logger):
        self.device = device
        self.config = config
        self.logger = logger
        self.miniprogram_config = config.get('miniprogram', {})

    def _dump_hierarchy(self):
        """获取当前界面的层级结构"""
        self.logger.info("正在分析界面元素...")
        
        # 尝试多种方式获取界面结构
        try:
            # 方法1: 标准dump_hierarchy
            xml = self.device.dump_hierarchy()
            self.logger.info("标准dump_hierarchy方法结果:")
            self.logger.info(f"界面结构大小: {len(xml)} 字符")
            self.logger.info(f"界面结构前300字符:\n{xml[:300]}...")
            
            # 方法2: 直接保存截图，不使用dump_hierarchy到文件
            screenshot_path = f"screen_{int(time.time())}.png"
            self.device.screenshot(screenshot_path)
            self.logger.info(f"已保存屏幕截图到: {screenshot_path}")
            
            # 方法3: 使用xpath检查是否可以找到一些常见元素
            self.logger.info("尝试使用xpath检查元素...")
            
            # 检查文本元素
            text_elements = self.device.xpath("//*[@text]").all()
            self.logger.info(f"找到 {len(text_elements)} 个带文本的元素")
            if text_elements:
                sample = min(5, len(text_elements))
                self.logger.info(f"前{sample}个文本元素:")
                for i in range(sample):
                    try:
                        self.logger.info(f"  - 文本: {text_elements[i].text}, 类名: {text_elements[i].attrib.get('class')}")
                    except:
                        self.logger.info(f"  - 无法获取元素{i}的属性")
                        
            # 检查可点击的元素
            clickable_elements = self.device.xpath("//*[@clickable='true']").all()
            self.logger.info(f"找到 {len(clickable_elements)} 个可点击元素")
            
            return xml
            
        except Exception as e:
            self.logger.error(f"分析界面结构时出错: {str(e)}")
            return ""

    def _ensure_wechat_running(self) -> bool:
        """确保微信正在运行"""
        package_name = self.miniprogram_config.get('package', 'com.tencent.mm')
        
        # 如果微信不在运行，启动它
        if self.device.app_current().get('package') != package_name:
            self.logger.info("启动微信...")
            self.device.app_start(package_name)
            time.sleep(2)  # 等待启动
        
        # 确保回到主界面
        self.logger.info("回到微信主界面...")
        self.device.press("home")
        time.sleep(1)
        self.device.app_start(package_name)
        time.sleep(2)
                
        # 检查是否成功启动
        if self.device.app_current().get('package') != package_name:
            self.logger.error("微信启动失败")
            return False
                
        return True

    def ensure_wechat_main_interface(self):
        """确保在微信主界面"""
        self.logger.info("回到微信主界面...")
        
        # 多次按返回键，确保回到主界面
        for _ in range(3):
            self.device.press("back")
            time.sleep(0.5)
        
        # 检查是否在主界面
        if not self._is_on_main_interface():
            # 如果不在主界面，尝试点击"微信"tab
            wechat_tab = self.device(text="微信", className="android.widget.TextView")
            if wechat_tab.exists:
                wechat_tab.click()
                time.sleep(1)
        
        return self._is_on_main_interface()

    def _is_on_main_interface(self):
        """检查是否在微信主界面"""
        # 检查底部导航栏是否存在
        tabs = ["微信", "通讯录", "发现", "我"]
        for tab in tabs:
            if not self.device(text=tab).exists:
                return False
        return True

    def find_discover_button(self):
        """查找并点击发现按钮"""
        self.logger.info("查找发现按钮...")
        
        # 确保在主界面
        if not self.ensure_wechat_main_interface():
            raise Exception("无法返回到微信主界面")
        
        # 尝试多种方式查找发现按钮
        discover_btn = None
        
        # 1. 通过文本查找
        discover_btn = self.device(text="发现")
        if not discover_btn.exists:
            # 2. 通过description查找
            discover_btn = self.device(description="发现")
        
        if not discover_btn.exists:
            # 3. 通过resourceId查找（可能的ID列表）
            possible_ids = [
                "com.tencent.mm:id/discover_tab",
                "com.tencent.mm:id/tab_discover",
                "com.tencent.mm:id/tab_3"
            ]
            for rid in possible_ids:
                discover_btn = self.device(resourceId=rid)
                if discover_btn.exists:
                    break
        
        if not discover_btn.exists:
            # 4. 通过相对位置查找（通常在底部导航栏的第三个位置）
            tab_container = self.device(className="android.widget.TabWidget")
            if tab_container.exists:
                tabs = tab_container.child(className="android.widget.TextView")
                if len(tabs) >= 3:
                    discover_btn = tabs[2]
        
        if not discover_btn or not discover_btn.exists:
            self._dump_hierarchy()  # 输出界面结构以供调试
            raise Exception("找不到'发现'按钮")
        
        # 点击发现按钮
        discover_btn.click()
        time.sleep(1)
        return True

    def _find_miniprogram_entry(self) -> bool:
        """找到并点击小程序入口
        Returns:
            bool: 是否成功找到并点击小程序入口
        """
        try:
            # 尝试直接通过文本查找
            miniprogram_btn = self.device(text="小程序")
            if miniprogram_btn.exists:
                self.logger.info("找到小程序入口，点击进入...")
                miniprogram_btn.click()
                self.logger.info("等待小程序页面加载（10秒）...")
                time.sleep(10)  # 等待页面完全加载
                return True
            
            # 尝试通过滚动查找
            max_swipes = 3
            for _ in range(max_swipes):
                # 向下滚动
                self.device.swipe(0.5, 0.8, 0.5, 0.2)
                time.sleep(0.5)
                
                miniprogram_btn = self.device(text="小程序")
                if miniprogram_btn.exists:
                    self.logger.info("找到小程序入口，点击进入...")
                    miniprogram_btn.click()
                    self.logger.info("等待小程序页面加载（10秒）...")
                    time.sleep(10)  # 等待页面完全加载
                    return True
                
            self.logger.error("无法找到小程序入口")
            return False
        
        except Exception as e:
            self.logger.error(f"查找小程序入口时出错: {str(e)}")
            return False

    def _find_miniprogram_by_grid(self, name: str) -> bool:
        """通过网格位置尝试查找小程序
        
        微信小程序界面通常按网格排列，我们尝试点击可能的位置
        
        Args:
            name: 小程序名称
        Returns:
            bool: 是否成功点击小程序
        """
        self.logger.info(f"通过网格位置尝试查找小程序: {name}")
        
        try:
            # 获取屏幕尺寸
            width, height = self.device.window_size()
            self.logger.info(f"屏幕尺寸: {width}x{height}")
            
            # 根据反馈优化的网格位置，将已知有效的位置（第4个位置）放在首位
            # 原第4个位置是 (width * 0.25, height * 0.4)，即第二行第一列
            optimized_grid_positions = [
                # 首先尝试已知有效的位置（第二行第一列）
                (width * 0.25, height * 0.4),
                
                # 然后尝试周围的位置（相邻位置可能也有小程序）
                (width * 0.5, height * 0.4),  # 第二行第二列
                (width * 0.25, height * 0.25), # 第一行第一列
                (width * 0.5, height * 0.25),  # 第一行第二列
                
                # 最后尝试其他位置
                (width * 0.75, height * 0.25), # 第一行第三列
                (width * 0.75, height * 0.4),  # 第二行第三列
                (width * 0.25, height * 0.55), # 第三行第一列
                (width * 0.5, height * 0.55),  # 第三行第二列
                (width * 0.75, height * 0.55), # 第三行第三列
            ]
            
            self.logger.info("使用优化后的网格位置查找...")
            
            # 尝试点击优化后的网格位置
            for i, (x, y) in enumerate(optimized_grid_positions):
                self.logger.info(f"尝试点击位置 {i+1}: ({x}, {y})")
                self.device.click(x, y)
                time.sleep(1)
                
                # 检查是否进入了小程序
                current_app = self.device.app_current()
                
                # 如果活动变化，可能已进入小程序
                if current_app.get('activity') != '.plugin.appbrand.ui.AppBrandPluginUI':
                    self.logger.info(f"可能已进入小程序，活动变化为: {current_app.get('activity')}")
                    return True
                
                # 按返回键回到小程序列表
                self.device.press("back")
                time.sleep(0.5)
            
            # 尝试滚动查找（如果前面没有找到）
            self.logger.info("未找到小程序，尝试滚动后查找...")
            self.device.swipe(width * 0.5, height * 0.8, width * 0.5, height * 0.3)
            time.sleep(0.5)
            
            # 滚动后只尝试前3个位置
            for i, (x, y) in enumerate(optimized_grid_positions[:3]):
                self.logger.info(f"滚动后尝试点击位置 {i+1}: ({x}, {y})")
                self.device.click(x, y)
                time.sleep(1)
                
                # 检查是否进入了小程序
                current_app = self.device.app_current()
                
                # 如果活动变化，可能已进入小程序
                if current_app.get('activity') != '.plugin.appbrand.ui.AppBrandPluginUI':
                    self.logger.info(f"可能已进入小程序，活动变化为: {current_app.get('activity')}")
                    return True
                
                # 按返回键回到小程序列表
                self.device.press("back")
                time.sleep(0.5)
            
            self.logger.error(f"无法通过网格位置找到小程序: {name}")
            return False
            
        except Exception as e:
            self.logger.error(f"通过网格查找小程序时出错: {str(e)}")
            return False

    def launch(self) -> bool:
        """启动小程序"""
        try:
            # 确保微信在运行
            if not self._ensure_wechat_running():
                return False
                
            # 确保在微信主界面
            if not self.ensure_wechat_main_interface():
                return False
            
            # 点击发现按钮
            discover_btn = self.device(text="发现")
            if not discover_btn.exists:
                self.logger.error("找不到发现按钮")
                return False
            discover_btn.click()
            time.sleep(0.5)
            
            # 找到并点击小程序入口
            if not self._find_miniprogram_entry():
                return False
            
            # 分析页面结构
            self.logger.info("开始分析小程序页面结构...")
            xml = self._dump_hierarchy()
            
            # 尝试验证是否真的是小程序页面
            self.logger.info("尝试验证是否进入小程序页面...")
            
            # 方法1: 检查页面上是否有"小程序"相关文本
            miniprogram_texts = ["小程序", "最近使用", "我的小程序", "搜索小程序"]
            found_text = False
            for text in miniprogram_texts:
                if self.device(text=text).exists:
                    self.logger.info(f"找到小程序页面元素: '{text}'")
                    found_text = True
                    
            # 方法2: 尝试获取当前活动的应用和界面信息
            current_app = self.device.app_current()
            self.logger.info(f"当前应用信息: {current_app}")
            
            # 确认是否在小程序页面
            is_miniprogram_page = (
                current_app.get('package') == 'com.tencent.mm' and
                current_app.get('activity') == '.plugin.appbrand.ui.AppBrandPluginUI'
            )
            
            self.logger.info(f"是否在小程序页面: {is_miniprogram_page}")
            
            if is_miniprogram_page:
                # 尝试通过网格位置查找胖东来小程序
                target_name = self.miniprogram_config.get('name', '胖东来')
                if self._find_miniprogram_by_grid(target_name):
                    self.logger.info(f"成功点击进入小程序: {target_name}")
                    return True
            
            self.logger.info("页面结构分析完成")
            return True
            
        except Exception as e:
            self.logger.error(f"启动小程序时发生错误: {str(e)}")
            return False 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.utils import get_display_name, get_peer_id, resolve_id

class TelegramKeywordBot:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logger()
        
        # 初始化客户端
        self.user_client = None
        self.bot_client = None
        
        # 编译正则表达式
        self.compiled_keywords = []
        self.compiled_exclude_keywords = []
        self.compile_keywords()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            self.logger.error(f'配置文件 {self.config_path} 不存在，请先创建配置文件')
            exit(1)
        except yaml.YAMLError as e:
            self.logger.error(f'配置文件格式错误: {e}')
            exit(1)
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f'保存配置文件失败: {e}')
    
    def setup_logger(self):
        """设置日志"""
        log_config = self.config.get('logger', {})
        log_path = log_config.get('path')
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        
        # 创建日志目录
        if log_path:
            log_dir = Path(log_path)
        else:
            log_dir = Path(__file__).parent / 'logs'
        
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f'telegram_bot_{datetime.now().strftime("%Y%m%d")}.log'
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 设置日志器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def compile_keywords(self):
        """编译正则表达式"""
        self.compiled_keywords = []
        self.compiled_exclude_keywords = []
        
        # 编译关注关键字
        for pattern in self.config.get('keyword', {}).get('keyword_list', []):
            try:
                # 处理 /pattern/flags 格式
                if pattern.startswith('/') and pattern.rfind('/') > 0:
                    last_slash = pattern.rfind('/')
                    regex_pattern = pattern[1:last_slash]
                    flags_str = pattern[last_slash + 1:]
                    
                    flags = 0
                    if 'i' in flags_str:
                        flags |= re.IGNORECASE
                    if 'm' in flags_str:
                        flags |= re.MULTILINE
                    if 's' in flags_str:
                        flags |= re.DOTALL
                    
                    compiled_pattern = re.compile(regex_pattern, flags)
                else:
                    compiled_pattern = re.compile(pattern)
                
                self.compiled_keywords.append(compiled_pattern)
            except re.error as e:
                self.logger.error(f'关键字正则表达式编译失败: {pattern}, 错误: {e}')
        
        # 编译排除关键字
        for pattern in self.config.get('keyword', {}).get('exclude_list', []):
            try:
                if pattern.startswith('/') and pattern.rfind('/') > 0:
                    last_slash = pattern.rfind('/')
                    regex_pattern = pattern[1:last_slash]
                    flags_str = pattern[last_slash + 1:]
                    
                    flags = 0
                    if 'i' in flags_str:
                        flags |= re.IGNORECASE
                    if 'm' in flags_str:
                        flags |= re.MULTILINE
                    if 's' in flags_str:
                        flags |= re.DOTALL
                    
                    compiled_pattern = re.compile(regex_pattern, flags)
                else:
                    compiled_pattern = re.compile(pattern)
                
                self.compiled_exclude_keywords.append(compiled_pattern)
            except re.error as e:
                self.logger.error(f'排除关键字正则表达式编译失败: {pattern}, 错误: {e}')
    
    async def init_clients(self):
        """初始化客户端"""
        account_config = self.config['account']
        proxy_config = self.config.get('proxy', {})
        
        # 设置代理
        proxy = None
        if proxy_config.get('type') and proxy_config.get('address') and proxy_config.get('port'):
            proxy = {
                'proxy_type': proxy_config['type'],
                'addr': proxy_config['address'],
                'port': proxy_config['port']
            }
        
        # 初始化用户客户端
        self.user_client = TelegramClient(
            'user_session',
            account_config['api_id'],
            account_config['api_hash'],
            proxy=proxy
        )
        
        # 初始化Bot客户端
        self.bot_client = TelegramClient(
            'bot_session',
            account_config['api_id'],
            account_config['api_hash'],
            proxy=proxy
        )
        
        # 启动用户客户端
        await self.user_client.start(phone=account_config['user_phone'])
        
        # 启动Bot客户端
        await self.bot_client.start(bot_token=account_config['bot_token'])
        
        self.logger.info("客户端初始化完成")
    
    def check_message_keywords(self, message_text: str):
        """检查消息是否匹配关键字"""
        if not message_text:
            return False
        
        matched_keyword = None

        # 检查是否匹配关注关键字
        keyword_matched = False
        for pattern in self.compiled_keywords:
            match = pattern.search(message_text)
            if match:
                keyword_matched = True
                matched_keyword = match.group()
                break
        
        if not keyword_matched:
            return False
        
        # 检查是否匹配排除关键字
        for pattern in self.compiled_exclude_keywords:
            if pattern.search(message_text):
                return False
        
        return matched_keyword
    
    def check_command_authorized(self, user_id: int) -> bool:
        """检查用户是否有权限发送命令"""
        return user_id in self.config.get('data', {}).get('command_id_list', [])
    
    def check_source_filter(self, source_id: int) -> bool:
        """检查是否应该过滤此数据源"""
        if not self.config.get('data', {}).get('source_filter', False):
            return False
        return source_id in self.config.get('data', {}).get('source_filter_block_list', [])
    
    def check_from_command_result(self, source_id: int) -> bool:
        """检查数据源是否来自命令或输出结果"""
        if source_id in self.config.get('data', {}).get('command_id_list', []):
            return True
        else:
            return self.check_from_result(source_id)

    def check_from_result(self, source_id: int) -> bool:
        """检查数据源是否来自输出结果"""
        return source_id in self.config.get('data', {}).get('result_id_list', [])

    async def send_notification(self, message: str):
        """发送通知消息"""
        result_ids = self.config.get('data', {}).get('result_id_list', [])
        
        for target_id in result_ids:
            try:
                await self.bot_client.send_message(target_id, message, link_preview = False,parse_mode = 'markdown')
                self.logger.info(f'通知已发送到 {target_id}')
            except Exception as e:
                self.logger.error(f'发送通知失败 {target_id}: {e}')
    
    async def handle_new_message(self, event):    
        """处理新消息"""
        try:
            message = event.message            
            
            chat_id = getattr(message, 'chat_id', None)
            if not chat_id:
                self.logger.debug("无法获取 chat_id, 忽略此消息")
                return
            # 前面得到的是 Peer ID, 需要转换一下, 与界面上看到的ID一致
            # 配置文件中, 使用的是界面上看到的ID
            source_id, peer_type = resolve_id(chat_id)

            self.logger.debug(f'收到新消息 - source_id={source_id}')

            # 检查是否临时屏蔽一些数据源
            if self.check_source_filter(source_id):
                return
            
            # 检查是否来自 命令, 或来自 输出结果
            if self.check_from_command_result(source_id):
                return
            
            sender = await message.get_sender()

            # 忽略来自机器人的消息
            if self.config.get('data', {}).get('block_bot_msg', True):
                if getattr(sender, 'bot', False):
                    self.logger.debug(f'忽略来自机器人的消息 - {sender.id}')
                    return
            
            message_text = message.text
            if message.file and message.file.name:
                message_text += ' {}'.format(message.file.name)  # 追加上文件名
            
            self.logger.debug(f'消息内容 - {message_text[:20]}')  # 只打印部分内容

            # 检查关键字
            regex_match_str = self.check_message_keywords(message_text)
            if not regex_match_str:
                self.logger.debug(f'消息不包含关键字')
                return

            # 获取聊天信息
            chat = await event.get_chat()
            chat_title = getattr(chat, 'title', getattr(chat, 'username', str(chat.id)))
            chat_username = getattr(chat, 'username', None)
            if chat_username:
                chat_info = f'(@{chat_username})'
                chat_url = f'https://t.me/{chat_username}/{message.id}'
            else:
                chat_info = f'({source_id})'
                chat_url = f'https://t.me/c/{source_id}/{message.id}'

            # 获取发送者信息
            sender_info = get_display_name(sender)
            if hasattr(sender, 'username') and sender.username:
                sender_info += f"(@{sender.username})"
            else:
                sender_info += f"({sender.id})"
                                
            # 构建通知消息
            notification = f'[#FOUND]({chat_url}) "**{regex_match_str}**" IN **{chat_title}**{chat_info} FROM {sender_info}'
            notification += f'\n{message_text[:200]}'
            
            await self.send_notification(notification)
            self.logger.info(f'检测到关键字消息: "{regex_match_str}" - {chat_title}{chat_info} - {sender_info}')
            
        except Exception as e:
            self.logger.error(f'处理消息时出错: {e}')
    
    async def handle_bot_commands(self, event):
        """处理Bot命令"""
        try:
            message = event.message
            cmd_sender_id = event.chat_id
            # 上一步得到的是 Peer ID, 需要转换一下, 与界面上看到的ID一致
            # 配置文件中, 使用的是界面上看到的ID
            cmd_sender_id, peer_type = resolve_id(cmd_sender_id)            

            self.logger.info(f'cmd_sender_id = {cmd_sender_id}')
                        
            # 如果命令不是来自 用户直接的消息, 那么应该忽略来自 输出结果中的群组和频道 的信息
            # 输出结果 列表可以包含 user, group, channel
            if peer_type is not PeerUser:
                if self.check_from_result(cmd_sender_id):
                    return

            # 检查权限
            if not self.check_command_authorized(cmd_sender_id):
                self.logger.info(f'({cmd_sender_id}) 没有权限使用此Bot')
                await event.reply(f'❌ ({cmd_sender_id}) 没有权限使用此Bot')
                return
            
            command_text = message.message.strip()
            
            if command_text.startswith('/start'):
                await event.reply("""✨ Telegram关键字监听Bot
                
🔧 可用命令:
/add_keyword <正则表达式> - 添加关注关键字
/remove_keyword <正则表达式> - 移除关注关键字
/add_exclude <正则表达式> - 添加排除关键字
/remove_exclude <正则表达式> - 移除排除关键字
/list_keywords - 查看所有关键字""")
            
            elif command_text.startswith('/add_keyword '):
                keyword = command_text[13:].strip()
                if keyword:
                    if 'keyword' not in self.config:
                        self.config['keyword'] = {}
                    if 'keyword_list' not in self.config['keyword']:
                        self.config['keyword']['keyword_list'] = []
                    self.config['keyword']['keyword_list'].append(keyword)

                    self.save_config()
                    self.compile_keywords()
                    await event.reply(f'✅ 已添加关注关键字: `{keyword}`')
                else:
                    await event.reply('❌ 请提供关键字')
            
            elif command_text.startswith('/remove_keyword '):
                keyword = command_text[16:].strip()
                if keyword and keyword in self.config.get('keyword', {}).get('keyword_list', []):
                    self.config['keyword']['keyword_list'].remove(keyword)

                    self.save_config()
                    self.compile_keywords()
                    await event.reply(f'✅ 已移除关注关键字: `{keyword}`')
                else:
                    await event.reply('❌ 关键字不存在')
            
            elif command_text.startswith('/add_exclude '):
                keyword = command_text[13:].strip()
                if keyword:
                    if 'keyword' not in self.config:
                        self.config['keyword'] = {}
                    if 'exclude_list' not in self.config['keyword']:
                        self.config['keyword']['exclude_list'] = []
                    self.config['keyword']['exclude_list'].append(keyword)

                    self.save_config()
                    self.compile_keywords()
                    await event.reply(f'✅ 已添加排除关键字: `{keyword}`')
                else:
                    await event.reply('❌ 请提供关键字')
            
            elif command_text.startswith('/remove_exclude '):
                keyword = command_text[16:].strip()
                if keyword and keyword in self.config.get('keyword', {}).get('exclude_list', []):
                    self.config['keyword']['exclude_list'].remove(keyword)

                    self.save_config()
                    self.compile_keywords()
                    await event.reply(f'✅ 已移除排除关键字: `{keyword}`')
                else:
                    await event.reply('❌ 关键字不存在')
            
            elif command_text.startswith('/list_keywords'):
                keywords = self.config.get('keyword', {}).get('keyword_list', [])
                exclude_keywords = self.config.get('keyword', {}).get('exclude_list', [])
                
                message_text = "📋 关键字列表\n\n"
                message_text += "🔍 关注关键字:\n"
                if keywords:
                    for i, kw in enumerate(keywords, 1):
                        message_text += f"{i}. `{kw}`\n"
                else:
                    message_text += "无\n"
                
                message_text += "\n🚫 排除关键字:\n"
                if exclude_keywords:
                    for i, kw in enumerate(exclude_keywords, 1):
                        message_text += f"{i}. `{kw}`\n"
                else:
                    message_text += "无\n"
                
                await event.reply(message_text)
            
            else:
                message_text = "❌非法命令或命令格式不正确"
                await event.reply(message_text)

        except Exception as e:
            self.logger.error(f'处理Bot命令时出错: {e}')
    
    async def start_monitoring(self):
        """开始监听"""
        try:
            await self.init_clients()
            
            # 注册事件处理器
            @self.user_client.on(events.NewMessage)
            async def user_message_handler(event):
                await self.handle_new_message(event)
            
            @self.bot_client.on(events.NewMessage)
            async def bot_message_handler(event):
                await self.handle_bot_commands(event)
            
            self.logger.info("开始监听消息...")
            print("Bot已启动, 正在监听消息...")
            
            # 保持运行
            await self.user_client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f'启动监听失败: {e}')
        finally:
            if self.user_client:
                await self.user_client.disconnect()
            if self.bot_client:
                await self.bot_client.disconnect()

async def main():
    bot = TelegramKeywordBot()
    await bot.start_monitoring()

if __name__ == '__main__':
    asyncio.run(main())

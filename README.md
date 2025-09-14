# tg-keyword-monitor-bot
Telegram 监控关键字机器人 基于 telethon

## 项目原理
登录一个telegram的用户, 在各个群组/频道中接收消息.  
当消息内容匹配关键字时, 控制一个telegram的机器人发出通知.

## 申请 api_id, api_hash 

https://my.telegram.org/apps

开通api 建议使用新注册的telegram账户  
担心万一玩大了 被封了

得到 api_id, api_hash
![chrome_2022-08-08_11-04-17](https://user-images.githubusercontent.com/665889/183333531-ea69d6c8-b720-4efa-9c6e-fc31f2b5a252.png)

## 申请 bot_token

https://t.me/BotFather

/start

/newbot

bot的name

bot的username

得到 bot_token

`插入图片`

## 部署

安装python  
一般你用的比较新版本的操作系统 Debian / Ubuntu, 已经自带了.   
略

安装 pip
```
apt install -y python3-pip
```

拉取本项目代码
```
apt install -y git
git clone https://github.com/crazypeace/tg-keyword-monitor-bot
cd tg-keyword-monitor-bot
```

安装python依赖
```
pip3 install -r requirements.txt --break-system-packages
```

修改配置文件  
`config.yaml.default` 复制为 `config.yaml`

修改配置文件`config.yaml`内容

* 注意配置文件中原有的单引号 ' ' 不要删掉了

api_id, api_hash, bot_token 参考下图填写

`插入图片`

user_phone 为开通api的telegram账户的电话号码

`插入图片`

## 第一次运行bot

```
python3 ./main.py
```

脚本窗口提示你输入验证码，同时，开通api的telegram账户会收到一个验证码

![image](https://user-images.githubusercontent.com/665889/183342317-6fd4e4a3-5670-4f97-b09c-11f8236024d8.png)

将这个验证码输入到脚本窗口
* 只有第一次运行时会需要验证码. 以后运行不需要输入验证码. 你会发现目录下多出来一个session文件

## 向bot发第一条命令

在你的 telegram 客户端上, 登录一个你作为本项目管理员的 telegram 账户.
* 可以使用申请api_id的telegram账户

通过bot_username找到你的bot,  

`插入图片`

发送命令 `/start`  
bot会回应 `<你的ID> 没有权限`

`插入图片`

## 配置文件添加 命令源 和 通知目的地

命令行 Ctrl+C 中断 bot 的运行.

修改配置文件`config.yaml`内容

command_id_list 和 result_id_list 的内容都修改为 `你的ID`
* 注意配置文件中原有的 - 不要删掉了
* 你现在命令源和通知目的都只有1个. 所以 command_id_list 和 result_id_list 下面都应该只有1行数据(即, 你的ID)

`插入图片`

再次启动bot
```
python3 ./main.py
```

试试看给bot发命令`/start`  
应该会有回应了

`插入图片`

## 设置关键字

可以通过bot命令交互, 也可以直接修改配置文件

`/keyword1|keyword2|keyword3/i` 的意思是  
`keyword1` 或 `keyword2` 或 `keyword3`, 忽略英文大小写

`极简|一键|脚本` 的意思是  
`极简` 或 `一键` 或 `脚本`

## 监控数据源

本项目监控的数据源来自 申请api的telegram账户 在群组和频道里收到的信息.  
你用telegram客户端 登录了 申请api的telegram账户 后, 自己去加你想监控的群组和频道.  
遇到入群验证, 正好可以人肉解决.

## 验证监控效果

你可以自己开个测试用的群, 把 申请api的telegram账户 拉进去, 然后随便发点 包含关键字 的信息.  
观察, 本项目管理员的telegram账户 是否收到了 bot 发的通知.

`插入图片`

## 长期运行bot

```
systemctl enable tg-bot.service
systemctl start tg-bot.service
```

* 如果你的目录不是`/root/tg-keyword-monitor-bot`, 那么请自行编辑tg-bot.service文件
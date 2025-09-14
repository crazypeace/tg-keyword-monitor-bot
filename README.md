# tg-keyword-monitor-bot
Telegram 监控关键字机器人 基于 telethon

## 项目原理
登录一个telegram的用户, 在各个群组/频道中接收消息.  
当消息内容匹配关键字时, 控制一个telegram的机器人发出通知.

建议新注册一个telegram账户来玩本项目 万一玩大了 被封了 影响较小

## 申请 api_id, api_hash 

https://my.telegram.org/apps

开通api 

得到 api_id, api_hash
![chrome_2022-08-08_11-04-17](https://user-images.githubusercontent.com/665889/183333531-ea69d6c8-b720-4efa-9c6e-fc31f2b5a252.png)

## 申请 bot_token

https://t.me/BotFather

/start

/newbot

提交 bot的name

提交 bot的username

得到 bot_token

<img width="562" height="366" alt="image" src="https://github.com/user-attachments/assets/39f63b51-75fc-4ee8-bddc-669fe015175d" />

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

<img width="1713" height="769" alt="image" src="https://github.com/user-attachments/assets/1478b729-0ee1-4f0c-8512-6c7195c05b38" />

user_phone 为telegram账户的电话号码

<img width="752" height="332" alt="image" src="https://github.com/user-attachments/assets/4aa531ce-ffe0-4cc4-a2c4-76330a3cb502" />

## 第一次运行bot

```
python3 ./main.py
```

命令行提示你输入验证码，同时，telegram账户会收到一个验证码

![image](https://user-images.githubusercontent.com/665889/183342317-6fd4e4a3-5670-4f97-b09c-11f8236024d8.png)

将这个验证码输入到命令行
* 只有第一次运行时会需要验证码. 以后运行不需要输入验证码. 你会发现目录下多出来一个session文件

## 向bot发第一条命令

在你的 telegram 客户端上, 登录 telegram 账户.

通过bot_username找到你的bot,  

<img width="1048" height="388" alt="image" src="https://github.com/user-attachments/assets/b2be5f10-011a-40df-ac57-aef90a7f3ef8" />

发送命令 `/start`  
bot会回应 `(你的ID) 没有权限`

<img width="846" height="323" alt="image" src="https://github.com/user-attachments/assets/fe0d2b07-417a-4963-b8a2-02b0897a5729" />

## 配置文件添加 命令源 和 通知目的地

命令行 Ctrl+C 中断 bot 的运行.

修改配置文件`config.yaml`内容

command_id_list 和 result_id_list 的内容都修改为 `你的ID`
* 注意配置文件中原有的 - 不要删掉了
* 你现在命令源和通知目的都只有1个. 所以 command_id_list 和 result_id_list 下面都应该只有1行数据(即, 你的ID)

<img width="982" height="412" alt="image" src="https://github.com/user-attachments/assets/19bf42b2-5b1a-4bad-9271-faf5b325c1ca" />

再次启动bot
```
python3 ./main.py
```

试试看给bot发命令`/start`  
应该会有回应了

<img width="853" height="368" alt="image" src="https://github.com/user-attachments/assets/4aa74a3e-d3a0-4c57-b872-68c883ce8761" />

## 设置关键字

可以通过bot命令交互, 也可以直接修改配置文件 `config.yaml`

`/keyword1|keyword2|keyword3/i` 的意思是  
`keyword1` 或 `keyword2` 或 `keyword3`, 忽略英文大小写

`极简|一键|脚本` 的意思是  
`极简` 或 `一键` 或 `脚本`

<img width="616" height="344" alt="image" src="https://github.com/user-attachments/assets/2b3f6de9-f71d-4ef5-8aa7-af71853afaf6" />

## 监控数据源

本项目监控的数据源来自 telegram账户 在群组和频道里收到的信息.  
你用telegram客户端 登录了 telegram账户 后, 自己去加你想监控的群组和频道.  
入群验证, 不公开群需要别人拉你, 需要管理员审批, ... 等等等等  这些问题, 需要你自己解决.

## 验证监控效果

你可以自己开个测试用的群, 然后随便发点 包含关键字 的信息.  
观察, telegram账户 是否收到了 bot 发的监控通知.

<img width="667" height="112" alt="image" src="https://github.com/user-attachments/assets/90d93fb7-5798-45b8-b851-a0c51f439f40" />

## 长期运行bot

```
cp tg-keyword-monitor-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
systemctl enable tg-keyword-monitor-bot.service
systemctl start tg-keyword-monitor-bot.service
```

* 如果你的目录不是`/root/tg-keyword-monitor-bot`, 那么请自行编辑tg-keyword-monitor-bot.service文件的内容

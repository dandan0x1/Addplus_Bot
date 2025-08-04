## 功能介绍
注册地址：https://addplus.org/boost/ariel_sands_dan

抓取cookie

<img width="1718" height="1102" alt="抓取cookie" src="https://github.com/user-attachments/assets/3cf3b47a-4322-4ed5-9359-0d3da203c8ef" />


这是一个用于 AddPlus 自动涨分，具有以下功能：

- 🍪 **Cookie 管理**：支持单账户手动输入和多账户文件批量管理
- 📊 **数据同步**：自动从服务器获取用户名数据
- 💾 **智能存储**：只保存新增的用户名数据到本地文件
- 🚀 **自动涨分**：批量发送涨分请求到 AddPlus 平台
- 📝 **实时日志**：显示详细的操作日志和状态信息
- 🔄 **多账户并发**：支持多个账户同时并发处理，提高效率

## 使用步骤

### 1. 启动工具

```bash
python bot.py
```

### 2. 选择运行模式

工具启动后会显示两种模式选择：

#### 模式1：单账户模式
- 手动输入单个Cookie
- 适合测试或少量账户使用

#### 模式2：多账户并发模式
- 从 `cookie.txt` 文件读取多个Cookie
- 支持多账户同时并发处理
- 大幅提高处理效率

### 3. 配置Cookie

#### 单账户模式
直接在命令行输入完整的Cookie字符串

#### 多账户模式
编辑 `cookie.txt` 文件，每行一个Cookie：

```
# AddPlus Cookie 配置文件
# 每行一个完整的Cookie字符串
session_id=abc123; user_token=xyz789; csrf_token=token123
session_id=def456; user_token=uvw012; csrf_token=token456
# 以 # 开头的行为注释，会被忽略
```

**获取 Cookie 的方法：**
1. 打开浏览器，访问 `https://addplus.org`
2. 按 F12 打开开发者工具
3. 切换到 Network 标签页
4. 刷新页面或进行任何操作
5. 找到任意请求，查看 Request Headers 中的 Cookie 字段
6. 复制完整的 Cookie 值

### 4. 自动处理流程

工具将自动执行以下流程：

1. **获取数据**：从服务器获取最新的用户名列表
2. **数据处理**：检查本地 `x_name.json` 文件，只保存新增的用户名
3. **发送请求**：为每个用户名发送涨分请求到 AddPlus 平台
4. **显示结果**：在控制台显示每个请求的成功/失败状态

### 5. 监控状态

- 📊 **状态显示**：实时显示当前处理状态
- 📝 **详细日志**：显示每个账户的处理进度和结果
- 🔄 **并发处理**：多账户模式下显示各账户的并发处理情况

## 文件说明

### client_username.json

存储用户名数据的本地文件，格式如下：

```json
[
  {
    "number": 1,
    "username": "testuser123"
  },
  {
    "number": 2,
    "username": "anotheruser456"
  }
]
```

### cookie.txt

多账户模式的Cookie配置文件，格式如下：

```
# AddPlus Cookie 配置文件
# 每行一个完整的Cookie字符串
# 以 # 开头的行为注释，会被忽略
# 空行也会被忽略

session_id=abc123def456; user_token=xyz789uvw012; csrf_token=token123
session_id=ghi789jkl012; user_token=mno345pqr678; csrf_token=token456
```

### 数据同步逻辑

- 工具会检查本地文件中的最大编号
- 只从 API 获取编号大于本地最大编号的新数据
- 避免重复处理已有的用户名

## 多账户并发特性

### 并发处理优势

- **提高效率**：多个账户同时处理，大幅减少总处理时间
- **负载分散**：将请求分散到多个账户，降低单账户请求频率
- **容错能力**：单个账户出错不影响其他账户继续处理
- **实时监控**：每个账户的处理状态独立显示

### 性能优化

- **线程池管理**：使用ThreadPoolExecutor进行高效的线程管理
- **请求延迟**：每个账户内部请求间隔1秒，避免过于频繁
- **线程安全**：使用锁机制确保日志输出的线程安全
- **资源控制**：线程数量等于账户数量，避免资源浪费

### 使用建议

- **账户数量**：建议同时使用3-10个账户，平衡效率和稳定性
- **Cookie有效性**：确保所有Cookie都是有效的，无效Cookie会影响整体效率
- **网络环境**：在稳定的网络环境下使用，避免网络波动影响并发处理

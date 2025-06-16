# AWS ELB 跨域问题解决指南

## 问题原因

1. **协议变化**: 本地 `http://` → AWS `https://`
2. **ELB代理**: 负载均衡器可能过滤CORS头
3. **域名变化**: `localhost` → 实际域名
4. **WebSocket升级**: `ws://` → `wss://`

## 解决步骤

### 1. 确保ELB配置正确

#### ALB (Application Load Balancer) 配置:
```
Target Group:
- Protocol: HTTP
- Port: 5050
- Health Check Path: /health

Listener:
- Protocol: HTTPS
- Port: 443
- SSL Certificate: 配置你的域名证书
```

### 2. 检查安全组

确保EC2安全组允许：
```
Inbound Rules:
- Type: HTTP, Port: 5050, Source: ALB Security Group
- Type: HTTPS, Port: 443, Source: 0.0.0.0/0
- Type: Custom TCP, Port: 5050, Source: ALB Security Group
```

### 3. 验证域名解析

确保你的域名正确指向ELB：
```bash
nslookup your-domain.com
# 应该返回ELB的地址
```

### 4. 测试WebSocket连接

```bash
# 测试HTTP连接
curl -I https://your-domain.com/health

# 测试WebSocket握手
curl -H "Upgrade: websocket" \
     -H "Connection: Upgrade" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     https://your-domain.com/socket.io/
```

### 5. 检查日志

在EC2上检查应用日志：
```bash
tail -f app.log
# 查看是否有CORS相关错误
```

## 常见问题

### 问题1: WebSocket连接失败
**解决**: 确保ELB支持WebSocket升级
- 在ALB中启用 "WebSocket support"

### 问题2: HTTPS混合内容错误
**解决**: 确保前端使用HTTPS连接
- 检查前端配置使用 `https://` 而不是 `http://`

### 问题3: 预检请求失败
**解决**: 已在代码中添加OPTIONS处理

## 部署检查清单

- [ ] ELB配置正确
- [ ] 安全组开放正确端口
- [ ] SSL证书配置
- [ ] 域名DNS解析
- [ ] 前端配置使用HTTPS
- [ ] 后端CORS配置更新
- [ ] WebSocket支持启用 
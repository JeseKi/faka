# 渠道管理模块 (Channel Management)

## 功能概述

渠道管理模块负责管理系统中的销售渠道。每个商品（Card）都必须关联到一个特定的渠道，而员工（Staff）用户也必须隶属于一个渠道。这使得系统能够实现数据隔离和权限控制。

## 公开接口

### 渠道模型 (Channel Model)
- `id`: 渠道唯一标识符 (int)
- `name`: 渠道名称 (str)
- `description`: 渠道描述 (str, 可选)

### API 端点

所有端点都位于 `/api/channels` 路径下。

#### 创建渠道
- **POST** `/`
- **权限**: 仅限管理员 (admin)
- **请求体**: `ChannelCreate`
- **响应**: `ChannelOut`

#### 获取渠道详情
- **GET** `/{channel_id}`
- **权限**: 管理员 (admin) 或员工 (staff)
- **响应**: `ChannelOut`

#### 获取渠道列表
- **GET** `/`
- **权限**: 管理员 (admin) 或员工 (staff)
- **查询参数**: 
  - `skip` (int, 默认 0)
  - `limit` (int, 默认 100)
- **响应**: `List[ChannelOut]`

#### 更新渠道
- **PUT** `/{channel_id}`
- **权限**: 仅限管理员 (admin)
- **请求体**: `ChannelUpdate`
- **响应**: `ChannelOut`

#### 删除渠道
- **DELETE** `/{channel_id}`
- **权限**: 仅限管理员 (admin)
- **响应**: `ChannelOut`

## 数据流

1. 管理员通过 API 创建渠道。
2. 管理员在创建员工用户时，为员工分配一个渠道。
3. 员工只能查看和管理自己渠道下的商品。
4. 在卡密验证和使用过程中，系统会检查操作者（如果是员工）的渠道与卡密所属商品的渠道是否一致。

## 用法示例

### 创建渠道
```bash
curl -X POST "http://localhost:8000/api/channels/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "线上渠道", "description": "官方网站销售渠道"}'
```

### 获取渠道列表
```bash
curl -X GET "http://localhost:8000/api/channels/" \
  -H "Authorization: Bearer <user_token>"
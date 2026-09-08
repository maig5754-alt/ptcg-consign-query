# PTCG 寄售包邮 · 参与商品查询

静态 H5 查询页：系列 / 稀有度快筛，数据写在本地 `data.js`，不调用线上数据库。

## 在线地址

部署 GitHub Pages 后访问：

`https://maig5754-alt.github.io/ptcg-consign-query/`

## 本地预览

用浏览器直接打开 `index.html`，或：

```bash
python3 -m http.server 8080
# 打开 http://127.0.0.1:8080/
```

## 新增 SPU（自己改）

1. 编辑 `data.js` 里的 `window.SPU_DATA` 数组。
2. **新商品插到数组最前面**（页面按数组顺序展示，越前越靠上）。
3. 字段（与飞书「活动参与SPU名单」一致，并多两个派生/展示字段）：

| 字段 | 说明 |
|---|---|
| `spu` | SPUID（字符串） |
| `name` | SPU名称 |
| `card` | 卡片名称 |
| `code` | 编号，如 `CSV10C-017`；可空 |
| `series` | 系列码，一般从编号前缀来，如 `CSV10C`；无编号用 `未标注` |
| `rarity` | 稀有度原文，多值可用逗号，如 `PR,RR` |
| `rarities` | 拆开后的数组，如 `["PR","RR"]`（可省略，页面会从 `rarity` 拆） |
| `img` | 主图 CDN URL；可先空，再跑抓图脚本补 |

示例（置顶一条）：

```js
window.SPU_DATA = [
  {
    "spu": "123",
    "name": "示例卡",
    "card": "示例卡",
    "code": "CSV10C-001",
    "series": "CSV10C",
    "rarity": "R",
    "rarities": ["R"],
    "img": "https://treasure.qiandaocdn.com/..."
  },
  // ...原有数据
];
```

4. 提交并 push 到 `main`，Pages 约 1 分钟更新。

系列 / 稀有度下拉选项会根据数据**自动生成**；新系列、新稀有度会出现在快筛里。选中某系列后，稀有度只显示该系列实际有的值。

## 新增 SPU（交给 AI / 脚本）

把新表或增量名单给我，或本地跑：

```bash
# 1) 用飞书表/本地 JSON 合并到 data.js（新数据置顶）
# 2) 抓主图
python3 tools/fetch_images.py
# 3) 合并图片 URL 回 data.js
python3 tools/merge_images.py
```

## 筛选说明

- 系列、稀有度均可选「全部」，可只选其一或同时选。
- 稀有度多值会拆开匹配（选 `RR` 能命中 `PR,RR`）。
- 商品不跳转详情；点击缩略图看大图。
- 图片走千岛 CDN，页面需联网才能出图；已加 `no-referrer` 规避防盗链。

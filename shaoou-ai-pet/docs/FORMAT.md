# 精灵图格式

本项目资源为 AI 生成、非官方同人动画。角色及原设定权利归原权利人；本项目与米哈游 / HoYoverse 无合作或背书关系。

## 图集

- PNG：assets/spritesheet-extended.png，RGBA，1536 × 2288。
- WebP：assets/spritesheet-extended.webp，同尺寸的备用资源。
- 布局：8 列 × 11 行；每格 192 × 208；图集格式版本 2。
- 索引：行、列均从 0 开始；原点位于左上角。
- 裁切：左边界 = columnIndex × 192，上边界 = rowIndex × 208，宽高固定为 192 × 208。
- 共 57 个动画帧、16 个方向帧；其余 15 格透明。

## 动画行

| 行索引 | 状态名称 | 有效帧数 | 说明 |
| --- | --- | --- | --- |
| 0 | idle | 6 | 日常膝上贴贴 |
| 1 | running-right | 8 | 背后哄好、过渡到正面拥抱 |
| 2 | running-left | 8 | 两人站立、握肩轻晃 |
| 3 | waving | 4 | waving 状态动画 |
| 4 | jumping | 5 | jumping 状态动画 |
| 5 | failed | 8 | failed 状态动画 |
| 6 | waiting | 6 | waiting 状态动画 |
| 7 | running | 6 | running 状态动画 |
| 8 | review | 6 | review 状态动画 |

每行从第 0 列依次播放到有效帧数减一，后面的透明格不得参与播放。状态名称用于宿主映射，其中 running-left 与 running-right 表示触发方向，画面表现为互动而非普通跑步。

manifest.json 的 previewDurationsMs 对应随仓库 GIF 的逐帧时长（毫秒）。它是预览播放参考，不声明宿主必须采用相同节奏。

## 视线方向

第 9 行：0°、22.5°、45°、67.5°、90°、112.5°、135°、157.5°。

第 10 行：180°、202.5°、225°、247.5°、270°、292.5°、315°、337.5°。

角度以屏幕上方为 0°，顺时针增加：90°向右、180°向下、270°向左。默认中性帧为第 0 行、第 0 列；它与 0°向上的方向帧不同。具体映射见 manifest.json 的 lookDirections。

## 预览与主资源

PNG 是保留完整透明度的主资源。GIF 和 MP4 使用便于观看的预览背景，不应替代透明图集。previews/right-story-stills.png 展示向右动作的几个阶段；完整循环见 running-right.gif。

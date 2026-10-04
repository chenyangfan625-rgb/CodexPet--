# 少偶·膝上贴贴 / ShaoOu AI Pet

> **AI 生成 · 非官方同人动画**
>
> 本项目的动画精灵图由生成式 AI 制作，并经人工指导、选稿与程序处理。**它并非米哈游 / HoYoverse 的原创动画、官方素材或授权产品，与其不存在合作、隶属或背书关系。**
>
> 桑多涅（Sandrone）、哥伦比娅（Columbina）及《原神》相关角色设计、名称和商标的原有权利属于米哈游 / HoYoverse 及相应权利人。本项目的 AI 制作声明不改变这些权利归属。

An **AI-generated, unofficial fan animation** featuring Sandrone and Columbina. This project is not an official miHoYo / HoYoverse production and is not affiliated with, authorized by, or endorsed by them. Original character designs and related rights remain with their respective owners.

这是一个双人陪伴动画资源项目：日常膝上贴贴，向左时两人站立握肩轻晃，向右时从背后拥抱哄好过渡到正面抱抱。公开版本为 **1.0.0**；精灵图采用 **v2 布局**。

## 动作预览

| 日常：膝上贴贴 | 向左：站立轻晃 | 向右：哄好抱抱 |
| --- | --- | --- |
| ![AI生成：膝上贴贴](previews/idle.gif) | ![AI生成：站立轻晃](previews/running-left.gif) | ![AI生成：背后哄好后正面拥抱](previews/running-right.gif) |

![AI生成动画的动作静帧](previews/motion-stills.png)

[完整动作 GIF](previews/all-states.gif) · [完整动作 MP4](previews/all-states.mp4) · [十六方向预览](previews/look-loop.gif)

## 下载与使用

- [透明 PNG 精灵图](assets/spritesheet-extended.png)：主资源，1536 × 2288，RGBA。
- [WebP 精灵图](assets/spritesheet-extended.webp)：备用格式。
- [manifest.json](manifest.json)：网格、状态、视线方向和预览时序。
- [格式说明](docs/FORMAT.md)：九种状态的行顺序和裁切方法。

资源为 8 列 × 11 行，每格 192 × 208。前九行是动画状态，最后两行是十六个视线方向；无效格保持透明。按单格边界裁切，不要将整张图集直接当成单帧播放。

这些资源按 ChatGPT Work Pets 的 v2 图集布局整理，也可用于你自行实现的精灵播放器。仓库提供动画资源，不包含独立桌宠程序；导入或接入方式取决于所用应用。GIF 和 MP4 用于预览，PNG 保留透明边缘。清单中的预览时序用于复现随仓库的 GIF，实际宿主可能使用自己的播放时序。

## 检查资源

需要 Python 3.10 或更新版本，以及 Pillow：

```sh
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

脚本检查文件校验和、图集布局、有效帧/透明空格、各状态 GIF 时序、PNG/WebP 像素一致性，以及常见本机路径和账户标识残留。它不联网，也不上传资源；技术检查不代表第三方授权。

本次结果见 [发布检查报告](qa/release-validation.json)。部分相邻视线方向变化较细微，AI 绘制的服饰细节可能与官方设定不同。

## AI 制作与权利说明

- 图像生成与编辑：OpenAI 图像生成工具；项目文档和校验脚本也由 AI 辅助整理。
- 人工参与：提出造型和动作要求、提供参考、选择并修订动画版本。
- 程序处理：提取与配准帧、去除绿幕残边、透明图集组装和预览输出。
- 本项目没有采用“官方原创”“米哈游制作”等署名；引用、展示或二次整理时，请保留 AI 生成及非官方说明。

[NOTICE.md](NOTICE.md) 说明角色来源和授权范围；[LICENSE](LICENSE) 仅覆盖仓库新编写的脚本与说明文档，不覆盖角色、商标或美术资源。[制作说明](docs/GENERATION.md) 记录整理过程。原始参考图片、参考视频、账户 ID、上传记录和个人路径不随公开包发布。

## 仓库内容

```text
assets/       最终透明精灵图
previews/     动作、方向及全状态预览
docs/         格式、AI 制作和 GitHub 发布说明
scripts/      本地资源校验脚本
qa/           不含个人信息的发布检查报告
manifest.json 状态与图集映射
checksums.json 发布文件 SHA-256 清单
```

[更新记录](CHANGELOG.md) · [GitHub 发布步骤和文案](docs/PUBLISH.md)

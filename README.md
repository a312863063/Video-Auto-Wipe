# Video-Auto-Wipe
&emsp;&emsp;Note：这个项目展示的是我在视频擦除方面的一些探索。目前已实现的功能有三个：字幕擦除，图标擦除和动态遮挡物擦除。目前仅分享了字幕擦除，图标擦除我担心有些不好的应用暂时未开源。后续我想实现的内容包括：广告擦除，背景人擦除和敏感内容擦除。相关介绍可以参阅<a href='http://www.seeprettyface.com/research_notes_page3.html#intership'>我的研究笔记</a>。<br />
&emsp;&emsp;注意，这个项目的开源协议为GPL-3.0，您可将其当作工具使用，但不建议您用在商业软件之中。<br />

# 效果预览
## 1. 字幕擦除
![Image text](https://github.com/a312863063/Video-Auto-Wipe/blob/main/pics/de-text/detext_9_ko.JPG)<br/>
<p align="center"><a href='http://www.seeprettyface.com/mp4/video-inpainting/detext_06.mp4' target='_blank'>查看视频</a></p><br/>
&emsp;&emsp;字幕擦除模型的功能是模型自动感知到视频中字幕的位置然后进行擦除，感知字幕的方法为具有统一样式的文字区域被视作字幕。<br/>
<br/><br/>

## 2. 图标擦除
![Image text](https://github.com/a312863063/Video-Auto-Wipe/blob/main/pics/de-logo/delogo_4.JPG)<br/>
<p align="center"><a href='http://www.seeprettyface.com/mp4/video-inpainting/delogo_04.mp4' target='_blank'>查看视频</a></p><br/>
&emsp;&emsp;图标擦除模型的功能是模型自动感知到视频中图标的位置然后进行擦除，感知图标的方法为在时域上静止不动的像素块被视作图标。<br/>
<br/><br/>

## 3. 动态图标擦除
![Image text](https://github.com/a312863063/Video-Auto-Wipe/blob/main/pics/de-dynamic-logo/de-dynamic-logo_1.JPG)<br/>
<p align="center"><a href='http://www.seeprettyface.com/mp4/video-inpainting/de_dynamic_logo.mp4' target='_blank'>查看视频</a></p><br/>
&emsp;&emsp;动态图标擦除模型的功能是模型自动感知到视频中动态图标的位置然后进行擦除，感知动态图标的方法为在时域上闪烁出现或动态移动的固定像素块被视作动态图标。<br/>
<br/><br/>

# 使用方法
### 1.环境配置
&emsp;&emsp;torch>1.0<br/>
&emsp;&emsp;其他的缺什么依赖就pip install xxx，需要的东西不多<br/><br/>

### 2.运行方法
&emsp;&emsp;下载预训练文件放在pretrained-weight文件夹里。<br/>
&emsp;&emsp;&emsp;&emsp;预训练模型下载地址：链接：https://pan.baidu.com/s/1JN9-8Glw_ozOrSMgBIyHOw 提取码：px0s <br/> <br/>
&emsp;&emsp;更多的输入样例下载地址：https://pan.baidu.com/s/1_tzmvIoEQi3h_24-ieZJ_Q 提取码：cnqf <br/><br/>
&emsp;&emsp;运行```python demo.py```。<br/><br/><br/><br/>

# 训练方法
## 训练数据
### 背景数据制作
&emsp;&emsp;1.基于搜集的300余部高清电影制作了2,709部电影片段数据集；<br/>
&emsp;&emsp;&emsp;&emsp;下载地址：https://pan.baidu.com/s/1CIgJmFmx5iR2JfgAyjVaeg  提取码：xb7o <br/><br/>
&emsp;&emsp;2.基于搜集的40余部综艺节目制作了864部综艺片段数据集；<br/>
&emsp;&emsp;&emsp;&emsp;下载地址：https://pan.baidu.com/s/1lJk6IIWlwxknAie0LlGYOg  提取码：9rd4 <br/><br/>

### 前景数据制作
&emsp;&emsp;1.字幕擦除：利用ImageDraw库生成随机样式、字体的文字，并模拟其变换；<br/>
&emsp;&emsp;2.图标擦除：利用ImageDraw库生成随机的像素区块，并模型时域一致性（固定在视频中的某一个区域）；<br/>
&emsp;&emsp;3.动态图标擦除：利用PR软件制作闪烁、跳跃等字幕的动态特效，模拟动态图标的场景。<br/>
<br/>
### 训练过程
&emsp;&emsp;第1步. 针对特定任务的时域感知训练，即让模型能感知到需被擦除的前景数据；<br/>
&emsp;&emsp;第2步. 融合进擦除模型，进行端到端的微调训练。<br/>
<br/><br/><br/>

# 后续计划
![Image text](https://github.com/a312863063/Video-Auto-Wipe/blob/main/pics/undo.png)<br/>
&emsp;&emsp;后续我想实现广告、人物和敏感内容擦除等方向。填补技术效果已经不错了，难点在于感知。图标感知可以利用区域一致性实现，字幕感知可以利用模式一致性实现。人物感知要如何实现？广告感知要如何实现？这种设计不能有缺漏，估计得<b>结合数据本身的规律</b>去做才行。。
<br/><br/>

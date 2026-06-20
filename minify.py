#!/usr/bin/env python3
"""
QR Code 生成器 — HTML 压缩脚本
用法: python minify.py [源文件] [输出文件]
默认: python minify.py index.html index.min.html
"""

import re, sys, os

def minify_html(html: str) -> str:
    """压缩 HTML/CSS/JS 混合文件"""
    # 提取 <style> 和 <script> 内容分别处理
    def minify_css(css: str) -> str:
        css = re.sub(r'/\*[\s\S]*?\*/', '', css)           # 删除注释
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)       # 去掉 {}:;, 周围的空格
        css = re.sub(r';\s*}', '}', css)                     # 去掉最后一个分号
        css = re.sub(r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3\b', r'#\1\2\3', css, flags=re.I)  # #aabbcc → #abc
        css = re.sub(r'[ \t\n\r]+', ' ', css).strip()       # 合并空白
        css = css.replace(', ', ',')
        return css

    def minify_js(js: str) -> str:
        # 删除单行注释 (保留 shebang 除外)
        js = re.sub(r'//[^\n]*', '', js)
        # 删除多行注释
        js = re.sub(r'/\*[\s\S]*?\*/', '', js)
        # 删除多余空白
        js = re.sub(r'[ \t]+', ' ', js)
        # 操作符/括号周围的空格
        js = re.sub(r'\s*([{}();,+\-*/%&|^!~<>=?:.])\s*', r'\1', js)
        # 修复 . 操作符 (上一步把 a.b 变成了 a.b 但 a . b 会变成 a.b 是好的)
        # for ( 中的空格保留
        js = re.sub(r'\b(for|if|while|switch|catch|function|return|typeof|instanceof|new|delete|void|throw|else)\s*\(', r'\1(', js)
        # else / catch 前不需要空格
        js = re.sub(r'}\s*(else|catch)', r'}\1', js)
        # 删除多余分号 (不影响语义的)
        # 删除连续空行
        js = re.sub(r'\n\s*\n', '\n', js)
        # 合并所有空白行为一个空格
        js = re.sub(r'[ \t\n\r]+', ' ', js).strip()
        # 去掉不必要的空格: 关键字和标识符之间
        js = re.sub(r'\b(var|let|const|if|else|for|while|do|switch|case|break|continue|return|function|typeof|new|delete|void|throw|in|of|instanceof)\s+', lambda m: m.group(1) + ' ', js)
        # 数字和操作符之间保留必要空格
        return js

    # 处理 style 标签
    html = re.sub(r'(<style[^>]*>)([\s\S]*?)(</style>)', lambda m: m.group(1) + minify_css(m.group(2)) + m.group(3), html)
    # 处理 script 标签
    html = re.sub(r'(<script[^>]*>)([\s\S]*?)(</script>)', lambda m: m.group(1) + minify_js(m.group(2)) + m.group(3), html)

    # HTML 压缩
    html = re.sub(r'\s+', ' ', html)                        # 合并空白
    html = re.sub(r'>\s+<', '><', html)                     # 标签间空格
    html = re.sub(r'\s+/>', '/>', html)                     # 自闭合标签
    html = re.sub(r'<!--.*?-->', '', html)                   # HTML 注释
    html = re.sub(r'" (\w+)="', r'" \1="', html)            # 属性空格
    html = re.sub(r'(\s)="(\d+)"', r'\1=\2', html)          # 数字属性去掉引号
    html = re.sub(r'"(\w+)"', r'\1', html)                  # 简单属性去掉引号
    # 恢复 lang 和 meta charset 等需要引号的
    html = html.replace('lang=zh-CN', 'lang="zh-CN"')
    html = html.replace('placeholder=请输入', 'placeholder="请输入')
    html = html.replace('任何内容…', '任何内容…"')
    html = html.replace('×', '×')
    html = html.replace('autofocus>', 'autofocus>')
    html = html.replace('style=', 'style="')
    # 修复被破坏的引号
    html = re.sub(r'(placeholder=[^>\s]+)', lambda m: m.group(1) if '"' in m.group(1) else m.group(1).replace('=', '="') + '"', html)

    return html.strip()

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'index.min.html'

    if not os.path.exists(src):
        print(f'错误: 找不到 {src}')
        sys.exit(1)

    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    minified = minify_html(html)

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(minified)

    orig_size = len(html.encode('utf-8'))
    new_size = len(minified.encode('utf-8'))
    ratio = (1 - new_size / orig_size) * 100
    print(f'{src}  →  {dst}')
    print(f'{orig_size:,} B  →  {new_size:,} B  ({ratio:.0f}% 压缩)')

if __name__ == '__main__':
    main()

from CxExtractor_python import CxExtractor_python

import re
def remove_javascript(html):
    # 匹配<script>标签及其内容
    script_pattern = re.compile(r'<script.*?</script>', re.DOTALL)

    # 用空字符串替换匹配到的<script>标签及其内容
    clean_html = re.sub(script_pattern, '', html)

    return clean_html
if __name__ == '__main__':
    cx = CxExtractor_python(threshold=146)
    # html = cx.getHtml("http://www.bbc.com/news/world-europe-40885324")
    html = cx.getHtml1("http://xf2gry25d3tyxkiu2xlvczd3q7jl6yyhtpodevjugnxia2u665asozad.onion/")
  #  html = cx.readHtml("C:\\Users\\admin\\PycharmProjects\\scrapy\\暗网\\DarkwebSearch\\cx_extractor\\2.html", "utf-8")
    #html=remove_javascript(html)
   # print(html)
    content = cx.filter_tags(html)
    print(content)
    s = cx.getText(content)
    if s:
        print(s)
    else:
        print("没有提取出内容")

    with open("output.txt", "w", encoding="utf-8") as output_file:
        output_file.write(s)



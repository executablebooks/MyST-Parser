tags
.
<html>
<head>
<title class="a b" other="x">Title of the document</title>
</head>
<body>
The content of the document......
</body>
</html>
.
Root('')
Tag('html')
Data('\n')
Tag('head')
Data('\n')
Tag('title', {'class': 'a b', 'other': 'x'})
Data('Title of the docu...')
Data('\n')
Data('\n')
Tag('body')
Data('\nThe content of t...')
Data('\n')
Data('\n')
.

un-closed tags
.
<div class="a">
<div class="b">
.
Root('')
Tag('div', {'class': 'a'})
Data('\n')
Tag('div', {'class': 'b'})
Data('\n')
.

xtag
.
<img src="img_girl.jpg" alt="Girl in a jacket" width="500" height="600"/>
.
Root('')
XTag('img', {'src': 'img_girl.jpg', 'alt': 'Girl in a jacket', 'width': '500', 'height': '600'})
Data('\n')
.

data
.
a
.
Root('')
Data('a\n')
.

declaration
.
<!DOCTYPE html>
.
Root('')
Declaration('DOCTYPE html')
Data('\n')
.

process information
.
<?xml-stylesheet ?>
.
Root('')
Pi('xml-stylesheet ?')
Data('\n')
.

entities
.
&amp;

&#123;
.
Root('')
Entity('amp')
Data('\n\n')
Char('123')
Data('\n')
.

comments
.
<!--This is a comment. Comments are not displayed in the browser
-->
.
Root('')
Comment('This is a comment...')
Data('\n')
.

admonition
.
<div class="admonition tip alert alert-warning">
<div class="admonition-title" style="font-weight: bold;">Tip</div>
parameter allows to get a deterministic results even if we
use some random process (i.e. data shuffling).
</div>
.
Root('')
Tag('div', {'class': 'admonition tip alert alert-warning'})
Data('\n')
Tag('div', {'class': 'admonition-title', 'style': 'font-weight: bold;'})
Data('Tip')
Data('\nparameter allows...')
Data('\n')
.

image
.
<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="200px">
<img src="img/fun-fish.png" alt="fishy" class="bg-primary mb-1" width="300px">
.
Root('')
VoidTag('img', {'src': 'img/fun-fish.png', 'alt': 'fishy', 'class': 'bg-primary mb-1', 'width': '200px'})
Data('\n')
VoidTag('img', {'src': 'img/fun-fish.png', 'alt': 'fishy', 'class': 'bg-primary mb-1', 'width': '300px'})
Data('\n')
.

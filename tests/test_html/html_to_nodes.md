empty
.

.
<container>
    <raw format="html" xml:space="preserve">
.

text
.
abc
.
<container>
    <raw format="html" xml:space="preserve">
        abc
.

normal HTML
.
<div></div>
.
<container>
    <raw format="html" xml:space="preserve">
        <div></div>
.

image no src
.
<img>
.
<container>
    <system_message>
        <paragraph>
            error
.

image
.
<img src="a">
.
<container>
    <Element first="a" name="image" position="0">
.

image unknown attribute
.
<img src="a" other="b">
.
<container>
    <Element first="a" name="image" position="0">
.

image known attributes
.
<img src="a" height="200px" class="a b" name="b" align="left">
.
<container>
    <Element first="a" name="image" position="0">
        :align: left
        :class: a b
        :height: 200px
        :name: b
.

multiple images
.
<img src="a">
<img src="b">
.
<container>
    <Element first="a" name="image" position="0">
    <Element first="b" name="image" position="0">
.

admonition no close
.
<div class="admonition">
.
<container>
    <Element first="Note" name="admonition" position="0">
        :class: admonition
.

admonition
.
<div class="admonition">
</div>
.
<container>
    <Element first="Note" name="admonition" position="0">
        :class: admonition
.

admonition attributes
.
<div class="admonition tip" name="aname">
</div>
.
<container>
    <Element first="Note" name="admonition" position="0">
        :class: admonition tip
        :name: aname
.

admonition div-title
.
<div class="admonition tip">
<div class="title">*Hallo*</div>
.
<container>
    <Element first="*Hallo*" name="admonition" position="0">
        :class: admonition tip
.

admonition p-title
.
<div class="admonition tip">
<p class="title">*Hallo*</p>
.
<container>
    <Element first="*Hallo*" name="admonition" position="0">
        :class: admonition tip
.

admonition title+content
.
<div class="admonition">
<div class="title">*Hallo*</div>
content
</div>
.
<container>
    <Element first="*Hallo*" name="admonition" position="0">
        :class: admonition
        
        content
.

admonition multiple
.
<div class="admonition">
<div class="title">first</div>
content 1
</div>
<div class="admonition">
<div class="title">second</div>
content 2
</div>
.
<container>
    <Element first="first" name="admonition" position="0">
        :class: admonition
        
        content 1
    <Element first="second" name="admonition" position="0">
        :class: admonition
        
        content 2
.

admonition with paragraphs
.
<div class="admonition">
<p>paragraph 1</p>
<p>paragraph 2</p>
</div>
.
<container>
    <Element first="Note" name="admonition" position="0">
        :class: admonition
        
        paragraph 1
        
        paragraph 2
.

nested
.
<div class="admonition">
<p>Some **content**</p>
  <div class="admonition tip">
  <div class="title">A *title*</div>
  <p>Paragraph 1</p>
  <p>Paragraph 2</p>
  </div>
</div>
.
<container>
    <Element first="Note" name="admonition" position="0">
        :class: admonition
        
        Some **content**
        
        <div class="admonition tip">
          <div class="title">A *title*</div>
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
          </div>
.

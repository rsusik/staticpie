---
route: ~~BASE_URL~~/second
title: Second article
template: index.html
author: Put your name
menu: 
    label: Second article
    order: 2
panel:
  - type: toc
    max_lvl: 2
summary: Another blog post here
date: 2021-07-07
tags:
    - art2
---

# Second article with the same content


## Lorem ipsum
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque scelerisque pulvinar quam, sed tristique sem mollis a. Donec facilisis dolor felis, eu blandit tellus laoreet a. In consequat quam eros, a accumsan dolor sodales a. Morbi quis volutpat dui. 

## def_list

First term
: First definition
: Second definition

Second term
: Third definition


Quisque a sollicitudin elit, quis semper nulla. Sed dapibus nisi dolor, et posuere nisl egestas at. Vestibulum sollicitudin congue tristique. Aliquam egestas ipsum a velit tincidunt, ut sagittis nibh laoreet. Nam vitae lobortis quam. Aenean efficitur sapien ac mi rhoncus, at porta orci efficitur. 


## abbr

The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium

## footnote

Pellentesque quis quam tellus [^1]. In ligula arcu, sollicitudin a posuere eu, sollicitudin et dolor [^2]. Nunc leo risus, ultricies eu consectetur ut, aliquam nec nisl. Suspendisse gravida metus purus, vel tempor [^3] ante faucibus vel.

[^1]: footnote explain
[^2]: Ut gravida enim et euismod molestie
[^3]: Mauris non maximus sapien.

Aliquam et bibendum diam, quis aliquet metus. Aliquam mollis lacus eu mi maximus varius. Ut gravida enim et euismod molestie. Ut feugiat porta risus a sodales. Ut bibendum rutrum varius. 

## pymdownx test

### pymdownx.magiclink
A link: http://google.com

Another link: http://sdfsdf.sdfsdf.com

Etiam vestibulum, urna at lacinia tristique, lectus lacus condimentum lectus, sit amet consequat ex velit bibendum erat. Praesent mollis rhoncus nibh, ultricies pellentesque justo ultrices ut. Mauris non maximus sapien. Donec nec velit rutrum, malesuada enim at, ornare odio. 

### pymdownx.mark
==smart==mark==

Praesent pretium interdum consequat. Fusce ante erat, interdum eu vehicula vel, porta eu libero. Pellentesque non ornare lectus. Donec id faucibus nunc, egestas aliquam lorem. Proin nunc ipsum, interdum nec consectetur eu, porttitor ac elit. Donec porttitor leo pharetra leo viverra, eget ornare turpis ornare.


### pymdownx.arithmatex

\$\$
p(h_j=1|\mathbf{v}) = \sigma\left(\sum_i w_{ij}v_i + c_j\right)
\$\$

To nie jest inline \\[3 < 4\sigma \\] rownanie

To jest inline \\( 3 < 4\sigma \\) rownanie

\begin{align}
    p(v_i=1|\mathbf{h}) & = \sigma\left(\sum_j w_{ij}h_j + b_i\right) \\
    p(h_j=1|\mathbf{v}) & = \sigma\left(\sum_i w_{ij}v_i + c_j\right)
\end{align}

Praesent semper, dui nec varius aliquam, dolor velit vehicula libero, sed cursus nunc lacus eu mi. Vestibulum malesuada commodo gravida. Proin in tellus eget arcu aliquet mattis ac sit amet nulla. Vestibulum porta felis ac commodo congue. Donec in magna eget enim auctor ultricies vel eu purus. 


### pymdownx.caret

^^Insert me^^

text^a\ superscript^

### pymdownx.details

??? optional-class "Summary"
    Here's some content.


### pymdownx.keys

++ctrl+alt+delete++

Nullam massa arcu, congue sed rhoncus non, consectetur non purus. Morbi ultrices mi eros, at euismod augue posuere sed. Mauris consequat ac mi sit amet facilisis. Nunc tristique lacus odio, et faucibus odio rhoncus et. Integer consequat eros ullamcorper semper cursus. Suspendisse aliquet, erat et tempor ornare, sapien quam tincidunt sapien, nec malesuada nibh augue non metus.


### pymdownx.superfences

```python
import foo
import boo.baz
import foo.bar.baz

class Foo:
   def __init__(self):
       self.foo = None
       self.bar = None
       self.baz = None
```

### pymdownx.tasklist

Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b
        + [x] item c
    * [X] item C
- [ ] item 2
- [ ] item 3

Etiam tortor nunc, ullamcorper nec nulla nec, sagittis venenatis arcu. Etiam ornare vehicula fringilla. In hendrerit blandit neque mattis tincidunt. In vel dui id lacus eleifend rhoncus. Maecenas magna tellus, consequat vel orci id, blandit finibus orci. In justo risus, gravida ut erat vitae, feugiat volutpat arcu. Morbi imperdiet tempus convallis. Pellentesque vehicula augue at urna aliquam, ut tempus erat bibendum.


### pymdownx.tilde

~~Delete me~~
CH~3~CH~2~OH
text~a\ subscript~


## Markdown table test


| Tables   |       Are     |  Cool |
|----------|:-------------:|------:|
| col 1 is |  left-aligned | $1600 |
| col 2 is |    centered   |   $12 |
| col 3 is | right-aligned |    $1 |


# Source code test

#### python
~~~~python
import markdown
content = "this is a test"
qwe = markdown(content)
~~~~

## C++
~~~~cpp
int fun(int a, int b) {
    return a + b;
}
~~~~

# Latex equation tests

## Direct

\$\$x = {-b \pm \sqrt{b^2-4ac} \over 2a}\$\$ 

## In html span tag

<span class="math display">\\[
y = \frac{a}{b}
\\]</span>

Second:
\\[
y = \frac{a}{b}
\\]

Quisque sit amet nisi vitae elit tristique iaculis. Morbi eros sem, posuere sed est ut, posuere sagittis ipsum. Etiam in volutpat leo. Praesent tempor tortor nec leo viverra hendrerit. Praesent vel nisl a ex tempor tincidunt. Suspendisse bibendum dictum diam, sed tristique lectus porttitor ac. Nam in lacus aliquam, hendrerit arcu dapibus, ultrices velit. Integer facilisis, elit sit amet fermentum gravida, enim est rhoncus nulla, eu luctus ipsum leo id felis. Aenean sagittis fermentum condimentum. Nam ultricies blandit lacinia. Sed libero lacus, pulvinar eget velit et, vulputate placerat dui. Duis at arcu tincidunt nulla lacinia hendrerit. Proin ut nulla sed nunc scelerisque ultrices fermentum et mauris. Integer eu sapien auctor nisl dignissim feugiat. Vestibulum sagittis nunc et tincidunt interdum.

# References
